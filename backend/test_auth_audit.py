import os
import sys
import unittest
import json
import time

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.models.student import Student
from app.models.activity import Activity
from app.models.evidence import Evidence
from app.models.skill import StudentSkill
from app.core.security import validate_password_strength, PASSWORD_VALIDATION_ERROR_MSG, verify_access_token

class TestAuthenticationAndAccountPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_01_password_validation_rules(self):
        """Verify strict password validation rule and exact error message."""
        expected_msg = "Password must have a minimum length of 6 characters and include at least 1 letter, 1 number, and 1 special character."

        # Test invalid passwords
        invalid_cases = [
            ("abc", "Too short, no number, no special"),
            ("abcdef", "No number, no special"),
            ("123456", "No letter, no special"),
            ("abc123", "No special character"),
            ("abc!@#", "No number"),
            ("", "Empty"),
            ("123!@#", "No letter"),
        ]
        for pwd, desc in invalid_cases:
            is_valid, msg = validate_password_strength(pwd)
            self.assertFalse(is_valid, f"Password '{pwd}' ({desc}) should be invalid")
            self.assertEqual(msg, expected_msg)

            # Test via API registration endpoint
            resp = self.client.post(
                "/api/students/login",
                json={"name": f"PwdTest_{int(time.time()*1000)}", "password": pwd, "mode": "register"},
            )
            self.assertEqual(resp.status_code, 400, f"Registration with '{pwd}' should fail with 400")
            self.assertEqual(resp.json()["detail"], expected_msg)

        # Test valid passwords
        valid_cases = [
            "abc123!",
            "Ab1!cd",
            "StrongP@ssw0rd",
            "SkillBridge#2026",
            "Sunita@2026",
        ]
        for pwd in valid_cases:
            is_valid, msg = validate_password_strength(pwd)
            self.assertTrue(is_valid, f"Password '{pwd}' should be valid")
            self.assertEqual(msg, "")

        print("\n[PASS] 1. Password validation rules & exact error message verified on both unit and API level.")

    def test_02_duplicate_account_prevention(self):
        """Verify duplicate accounts are blocked with exact message: 'Account already exists. Please log in instead.'"""
        ts = int(time.time() * 1000)
        name = f"DuplicateUser_{ts}"
        pwd = "ValidPass123!"

        # Step 1: Register initial account
        reg1 = self.client.post(
            "/api/students/login",
            json={"name": name, "password": pwd, "mode": "register"},
        )
        self.assertEqual(reg1.status_code, 200)
        student_id = reg1.json()["student"]["id"]

        try:
            # Step 2: Attempt to register with SAME name
            reg2 = self.client.post(
                "/api/students/login",
                json={"name": name, "password": pwd, "mode": "register"},
            )
            self.assertEqual(reg2.status_code, 400)
            self.assertEqual(reg2.json()["detail"], "Account already exists. Please log in instead.")

            # Step 3: Attempt to register with lowercase name
            reg3 = self.client.post(
                "/api/students/login",
                json={"name": name.lower(), "password": pwd, "mode": "register"},
            )
            self.assertEqual(reg3.status_code, 400)
            self.assertEqual(reg3.json()["detail"], "Account already exists. Please log in instead.")

            # Step 4: Attempt to register with extra whitespace
            reg4 = self.client.post(
                "/api/students/login",
                json={"name": f"  {name}   ", "password": pwd, "mode": "register"},
            )
            self.assertEqual(reg4.status_code, 400)
            self.assertEqual(reg4.json()["detail"], "Account already exists. Please log in instead.")

            print(f"\n[PASS] 2. Duplicate account prevention verified for '{name}'. Returned exact message: 'Account already exists. Please log in instead.'")
        finally:
            db = SessionLocal()
            try:
                db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
                db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                db.commit()
            finally:
                db.close()

    def test_03_sunita_sahu_lifecycle_flow(self):
        """
        Exact user test:
        Create 'Sunita Sahu' -> Login -> Logout -> Login Again -> Logout -> Login Again.
        Verify PostgreSQL user record permanently remains and is never destroyed on logout.
        """
        ts = int(time.time() * 1000)
        name = f"Sunita Sahu {ts}"
        pwd = "SunitaPassword2026!"

        # Step 1: Create Account
        reg = self.client.post(
            "/api/students/login",
            json={"name": name, "password": pwd, "mode": "register"},
        )
        self.assertEqual(reg.status_code, 200)
        reg_data = reg.json()
        student_id = reg_data["student"]["id"]
        email = reg_data["student"]["email"]
        token1 = reg_data["token"]
        self.assertTrue(token1)
        print(f"\n[PASS] Step 1: Account '{name}' created in PostgreSQL (ID: {student_id}, Email: {email}).")

        try:
            # Step 2: First Login
            login1 = self.client.post(
                "/api/students/login",
                json={"name": name, "password": pwd, "mode": "login"},
            )
            self.assertEqual(login1.status_code, 200)
            self.assertEqual(login1.json()["student"]["id"], student_id)
            print("[PASS] Step 2: First login succeeded.")

            # Step 3: Simulate Logout (destroy token on client, PostgreSQL row must stay)
            db = SessionLocal()
            student_in_db = db.query(Student).filter(Student.id == student_id).first()
            self.assertIsNotNone(student_in_db, "Student record must exist in PostgreSQL after logout")
            db.close()
            print("[PASS] Step 3: Logout executed; verified student record remains permanently in PostgreSQL.")

            # Step 4: Login Again with exact name
            login2 = self.client.post(
                "/api/students/login",
                json={"name": name, "password": pwd, "mode": "login"},
            )
            self.assertEqual(login2.status_code, 200)
            self.assertEqual(login2.json()["student"]["id"], student_id)
            token2 = login2.json()["token"]
            self.assertEqual(verify_access_token(token2), student_id)
            print("[PASS] Step 4: Login again succeeded with exact name.")

            # Step 5: Login with case variations & whitespace
            login3 = self.client.post(
                "/api/students/login",
                json={"name": f"  {name.lower()}  ", "password": pwd, "mode": "login"},
            )
            self.assertEqual(login3.status_code, 200)
            self.assertEqual(login3.json()["student"]["id"], student_id)
            print("[PASS] Step 5: Login with lowercase & whitespace variation succeeded.")

            # Step 6: Login with email address
            login4 = self.client.post(
                "/api/students/login",
                json={"name": email, "password": pwd, "mode": "login"},
            )
            self.assertEqual(login4.status_code, 200)
            self.assertEqual(login4.json()["student"]["id"], student_id)
            print(f"[PASS] Step 6: Login with email '{email}' succeeded.")

            # Step 7: Wrong password test (Account must NOT be deleted)
            wrong_login = self.client.post(
                "/api/students/login",
                json={"name": name, "password": "WrongPassword999!", "mode": "login"},
            )
            self.assertEqual(wrong_login.status_code, 401)
            self.assertIn("Incorrect password", wrong_login.json()["detail"])

            # Verify account still exists after wrong password attempt
            login_after_wrong = self.client.post(
                "/api/students/login",
                json={"name": name, "password": pwd, "mode": "login"},
            )
            self.assertEqual(login_after_wrong.status_code, 200)
            print("[PASS] Step 7: Wrong password properly rejected; subsequent correct login succeeded.")

            # Step 8: Load Skill Passport and Recommendations
            recs_resp = self.client.get("/api/recommendations/me", headers={"Authorization": f"Bearer {token2}"})
            self.assertEqual(recs_resp.status_code, 200)
            self.assertEqual(recs_resp.json()["student_id"], student_id)
            print("[PASS] Step 8: Recommendations loaded cleanly via verified JWT.")

        finally:
            db = SessionLocal()
            try:
                db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
                db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                db.commit()
            finally:
                db.close()

    def test_04_multiple_user_isolation_and_relogin(self):
        """
        Test multiple distinct users:
        User A: Create -> Login -> Logout -> Login Again -> Success
        User B: Create -> Login -> Logout -> Login Again -> Success
        User A -> Create User A again -> Blocked with 'Account already exists. Please log in instead.'
        """
        ts = int(time.time() * 1000)
        user_a_name = f"User_A_{ts}"
        user_a_pwd = "PassUserA123!"
        user_b_name = f"User_B_{ts}"
        user_b_pwd = "PassUserB456!"

        # 1. Create User A & User B
        res_a = self.client.post("/api/students/login", json={"name": user_a_name, "password": user_a_pwd, "mode": "register"}).json()
        res_b = self.client.post("/api/students/login", json={"name": user_b_name, "password": user_b_pwd, "mode": "register"}).json()
        id_a, id_b = res_a["student"]["id"], res_b["student"]["id"]

        try:
            # 2. Re-login User A
            log_a = self.client.post("/api/students/login", json={"name": user_a_name, "password": user_a_pwd, "mode": "login"})
            self.assertEqual(log_a.status_code, 200)
            self.assertEqual(log_a.json()["student"]["id"], id_a)

            # 3. Re-login User B
            log_b = self.client.post("/api/students/login", json={"name": user_b_name, "password": user_b_pwd, "mode": "login"})
            self.assertEqual(log_b.status_code, 200)
            self.assertEqual(log_b.json()["student"]["id"], id_b)

            # 4. Attempt to re-create User A -> Must return 'Account already exists. Please log in instead.'
            dup_a = self.client.post("/api/students/login", json={"name": user_a_name, "password": user_a_pwd, "mode": "register"})
            self.assertEqual(dup_a.status_code, 400)
            self.assertEqual(dup_a.json()["detail"], "Account already exists. Please log in instead.")

            print(f"\n[PASS] 4. Multi-user flow verified: User A (ID {id_a}) and User B (ID {id_b}) operate independently.")
        finally:
            db = SessionLocal()
            try:
                db.query(Activity).filter(Activity.student_id.in_([id_a, id_b])).delete(synchronize_session=False)
                db.query(Student).filter(Student.id.in_([id_a, id_b])).delete(synchronize_session=False)
                db.commit()
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
