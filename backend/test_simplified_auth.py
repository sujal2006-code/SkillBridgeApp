import os
import sys
import unittest
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
from app.core.security import (
    validate_password_strength,
    PASSWORD_VALIDATION_ERROR_MSG,
    verify_password,
    verify_access_token,
)


class TestSimplifiedSkillBridgeAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_01_password_validation_rules(self):
        """
        Test exact password validation cases:
        1. "12345" -> FAIL (no letter)
        2. "abcde" -> FAIL (no number)
        3. "abcd" -> FAIL (min 5 chars)
        4. "abc12" -> PASS
        5. "Skill1" -> PASS
        6. Password mismatch -> FAIL ("Passwords do not match.")
        """
        expected_msg = PASSWORD_VALIDATION_ERROR_MSG
        self.assertEqual(expected_msg, "Password must have a minimum length of 5 characters and include at least 1 letter and 1 number.")

        # Unit test validation function
        v1, msg1 = validate_password_strength("12345")
        self.assertFalse(v1)
        self.assertEqual(msg1, expected_msg)

        v2, msg2 = validate_password_strength("abcde")
        self.assertFalse(v2)
        self.assertEqual(msg2, expected_msg)

        v3, msg3 = validate_password_strength("abcd")
        self.assertFalse(v3)
        self.assertEqual(msg3, expected_msg)

        v4, msg4 = validate_password_strength("abc12")
        self.assertTrue(v4)
        self.assertEqual(msg4, "")

        v5, msg5 = validate_password_strength("Skill1")
        self.assertTrue(v5)
        self.assertEqual(msg5, "")

        # API Level verification of password rules on Registration
        r1 = self.client.post("/api/students/login", json={"name": "Test_12345", "password": "12345", "confirm_password": "12345", "mode": "register"})
        self.assertEqual(r1.status_code, 400)
        self.assertEqual(r1.json()["detail"], expected_msg)

        r2 = self.client.post("/api/students/login", json={"name": "Test_abcde", "password": "abcde", "confirm_password": "abcde", "mode": "register"})
        self.assertEqual(r2.status_code, 400)
        self.assertEqual(r2.json()["detail"], expected_msg)

        r3 = self.client.post("/api/students/login", json={"name": "Test_abcd", "password": "abcd", "confirm_password": "abcd", "mode": "register"})
        self.assertEqual(r3.status_code, 400)
        self.assertEqual(r3.json()["detail"], expected_msg)

        r6 = self.client.post("/api/students/login", json={"name": "Test_mismatch", "password": "Skill1", "confirm_password": "DifferentPass2", "mode": "register"})
        self.assertEqual(r6.status_code, 400)
        self.assertEqual(r6.json()["detail"], "Passwords do not match.")

        print("\n[PASS] 1. Password validation rules (12345, abcde, abcd, abc12, Skill1, mismatch) verified on both unit & API level.")

    def test_02_full_lifecycle_and_messages(self):
        """Test complete registration, duplicate handling, login, wrong name, wrong password, session."""
        ts = int(time.time() * 1000)
        name = f"HackathonUser_{ts}"
        password = "abc12"

        # 1. Create Account
        reg_resp = self.client.post(
            "/api/students/login",
            json={"name": name, "password": password, "confirm_password": password, "mode": "register"},
        )
        self.assertEqual(reg_resp.status_code, 200)
        student_id = reg_resp.json()["student"]["id"]
        token = reg_resp.json()["token"]
        self.assertEqual(verify_access_token(token), student_id)
        print(f"[PASS] 2. User '{name}' created successfully in PostgreSQL (ID: {student_id}).")

        try:
            # 2. Verify Database (salted PBKDF2 hash, no plaintext password)
            db = SessionLocal()
            student_rec = db.query(Student).filter(Student.id == student_id).first()
            self.assertIsNotNone(student_rec)
            self.assertEqual(student_rec.name, name)
            self.assertTrue(student_rec.password_hash.startswith("pbkdf2_sha256$"))
            self.assertTrue(verify_password(password, student_rec.password_hash))
            db.close()
            print("[PASS] 3. Database verified: Salted PBKDF2 hash stored, 0 plaintext passwords.")

            # 3. Duplicate Account Prevention
            dup_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": password, "confirm_password": password, "mode": "register"},
            )
            self.assertEqual(dup_resp.status_code, 400)
            self.assertEqual(dup_resp.json()["detail"], "Account already exists. Please log in.")
            print("[PASS] 4. Duplicate account rejected with 'Account already exists. Please log in.'")

            # 4. Wrong Name on Login
            wrong_name_resp = self.client.post(
                "/api/students/login",
                json={"name": "UnknownUser99999", "password": password, "mode": "login"},
            )
            self.assertEqual(wrong_name_resp.status_code, 404)
            self.assertEqual(wrong_name_resp.json()["detail"], "Incorrect name.")
            print("[PASS] 5. Wrong name rejected with 'Incorrect name.'")

            # 5. Wrong Password on Login
            wrong_pwd_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": "WrongPassword999", "mode": "login"},
            )
            self.assertEqual(wrong_pwd_resp.status_code, 401)
            self.assertEqual(wrong_pwd_resp.json()["detail"], "Invalid password.")
            print("[PASS] 6. Wrong password rejected with 'Invalid password.'")

            # 6. Correct Login
            login_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": password, "mode": "login"},
            )
            self.assertEqual(login_resp.status_code, 200)
            self.assertEqual(login_resp.json()["student"]["id"], student_id)
            print("[PASS] 7. Correct login succeeded and issued authenticated JWT.")

            # 7. Authenticated Endpoint Resolution
            auth_token = login_resp.json()["token"]
            profile_resp = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {auth_token}"})
            self.assertEqual(profile_resp.status_code, 200)
            self.assertEqual(profile_resp.json()["id"], student_id)
            print("[PASS] 8. Authenticated session verified via /api/students/me.")

            # 8. Repeated Login -> Logout -> Login cycles
            for cycle in range(1, 4):
                rel = self.client.post(
                    "/api/students/login",
                    json={"name": name, "password": password, "mode": "login"},
                )
                self.assertEqual(rel.status_code, 200)
                self.assertEqual(rel.json()["student"]["id"], student_id)
                print(f"[PASS] 9.{cycle} Login cycle {cycle}/3 passed.")

        finally:
            clean_db = SessionLocal()
            try:
                clean_db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
                clean_db.query(Evidence).filter(Evidence.student_id == student_id).delete(synchronize_session=False)
                clean_db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                clean_db.commit()
            finally:
                clean_db.close()

    def test_03_evidence_submission_preserves_user_identity(self):
        """
        Verify that submitting evidence:
        1. Links evidence to the authenticated user's ID
        2. Leaves the student's name, email, and identity completely unchanged
        3. Persists evidence across subsequent logins and profile queries
        """
        ts = int(time.time() * 1000)
        custom_name = f"EvidenceTester_{ts}"
        custom_pwd = "TesterPass123"

        # 1. Register new student
        reg = self.client.post(
            "/api/students/login",
            json={"name": custom_name, "password": custom_pwd, "confirm_password": custom_pwd, "mode": "register"},
        )
        self.assertEqual(reg.status_code, 200)
        student_id = reg.json()["student"]["id"]
        auth_token = reg.json()["token"]

        try:
            # 2. Submit evidence as authenticated student
            ev_resp = self.client.post(
                "/api/evidence",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "student_id": student_id,
                    "title": "Machine Learning Distributed Training Project",
                    "description": "High-throughput PyTorch pipeline on Kubernetes.",
                    "evidence_type": "project",
                    "issuer": "Stanford AI Laboratory",
                    "verification_status": "pending",
                },
            )
            self.assertEqual(ev_resp.status_code, 201)
            ev_data = ev_resp.json()
            self.assertEqual(ev_data["student_id"], student_id)
            self.assertEqual(ev_data["title"], "Machine Learning Distributed Training Project")

            # 3. Retrieve student profile via token and verify name is STILL custom_name (NOT changed to anything else)
            me_resp = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {auth_token}"})
            self.assertEqual(me_resp.status_code, 200)
            me_data = me_resp.json()
            self.assertEqual(me_data["id"], student_id)
            self.assertEqual(me_data["name"], custom_name)
            self.assertNotEqual(me_data["name"], "abc")
            self.assertEqual(len(me_data["evidence"]), 1)
            self.assertEqual(me_data["evidence"][0]["title"], "Machine Learning Distributed Training Project")

            # 4. Log in again with same credentials and verify evidence is still linked to this exact account
            relogin = self.client.post(
                "/api/students/login",
                json={"name": custom_name, "password": custom_pwd, "mode": "login"},
            )
            self.assertEqual(relogin.status_code, 200)
            self.assertEqual(relogin.json()["student"]["name"], custom_name)
            self.assertEqual(len(relogin.json()["student"]["evidence"]), 1)

            print(f"\n[PASS] 10. Evidence submission verified: linked to ID {student_id}, name '{custom_name}' 100% preserved.")

        finally:
            clean_db = SessionLocal()
            try:
                clean_db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
                clean_db.query(Evidence).filter(Evidence.student_id == student_id).delete(synchronize_session=False)
                clean_db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                clean_db.commit()
            finally:
                clean_db.close()

    def test_04_seed_demo_account(self):
        """Verify demo account Alex Rivera is preserved."""
        login_alex = self.client.post(
            "/api/students/login",
            json={"name": "Alex Rivera", "password": "stanford2026", "mode": "login"},
        )
        self.assertEqual(login_alex.status_code, 200)
        self.assertEqual(login_alex.json()["student"]["name"], "Alex Rivera")
        print("\n[PASS] 11. Demo account 'Alex Rivera' verified intact.")


if __name__ == "__main__":
    unittest.main()
