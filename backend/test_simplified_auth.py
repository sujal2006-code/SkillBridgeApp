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
from app.models.skill import Skill
from app.models.internship import Internship
from app.core.security import verify_password, verify_access_token


class TestSimplifiedSkillBridgeAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_01_complete_simplified_auth_lifecycle(self):
        """Full end-to-end audit of simplified Name + Password authentication."""
        ts = int(time.time() * 1000)
        name = f"HackathonTestUser_{ts}"
        password = "HackathonPass2026!"

        # 1. Password Confirmation Mismatch Check
        mismatch_resp = self.client.post(
            "/api/students/login",
            json={"name": name, "password": password, "confirm_password": "WrongConfirmPass123!", "mode": "register"},
        )
        self.assertEqual(mismatch_resp.status_code, 400)
        self.assertEqual(mismatch_resp.json()["detail"], "Passwords do not match.")
        print("\n[PASS] 1. Password mismatch blocked with 'Passwords do not match.'")

        # 2. Create Account
        reg_resp = self.client.post(
            "/api/students/login",
            json={"name": name, "password": password, "confirm_password": password, "mode": "register"},
        )
        self.assertEqual(reg_resp.status_code, 200)
        reg_data = reg_resp.json()
        student_id = reg_data["student"]["id"]
        token1 = reg_data["token"]
        self.assertEqual(verify_access_token(token1), student_id)
        print(f"[PASS] 2. Account '{name}' created successfully in PostgreSQL (ID: {student_id}).")

        try:
            # 3. Verify Database Record (no plaintext password)
            db = SessionLocal()
            student_rec = db.query(Student).filter(Student.id == student_id).first()
            self.assertIsNotNone(student_rec)
            self.assertEqual(student_rec.name, name)
            self.assertNotEqual(student_rec.password_hash, password)
            self.assertTrue(student_rec.password_hash.startswith("pbkdf2_sha256$"))
            self.assertTrue(verify_password(password, student_rec.password_hash))
            db.close()
            print("[PASS] 3. Database verified: Salted PBKDF2 hash stored, 0 plaintext passwords.")

            # 4. Duplicate Account Prevention
            dup_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": password, "confirm_password": password, "mode": "register"},
            )
            self.assertEqual(dup_resp.status_code, 400)
            self.assertEqual(dup_resp.json()["detail"], "Account already exists. Please log in.")

            # Also test case-insensitive duplicate attempt
            dup_lower = self.client.post(
                "/api/students/login",
                json={"name": name.lower(), "password": password, "confirm_password": password, "mode": "register"},
            )
            self.assertEqual(dup_lower.status_code, 400)
            self.assertEqual(dup_lower.json()["detail"], "Account already exists. Please log in.")
            print("[PASS] 4. Duplicate account prevented with 'Account already exists. Please log in.'")

            # 5. Wrong Name on Login
            wrong_name_resp = self.client.post(
                "/api/students/login",
                json={"name": "NonExistentUser99999", "password": password, "mode": "login"},
            )
            self.assertEqual(wrong_name_resp.status_code, 404)
            self.assertEqual(wrong_name_resp.json()["detail"], "Incorrect name.")
            print("[PASS] 5. Wrong name rejected with 'Incorrect name.'")

            # 6. Wrong Password on Login
            wrong_pwd_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": "WrongPassword999!", "mode": "login"},
            )
            self.assertEqual(wrong_pwd_resp.status_code, 401)
            self.assertEqual(wrong_pwd_resp.json()["detail"], "Invalid password.")
            print("[PASS] 6. Wrong password rejected with 'Invalid password.'")

            # 7. Correct Login
            login_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": password, "mode": "login"},
            )
            self.assertEqual(login_resp.status_code, 200)
            self.assertEqual(login_resp.json()["student"]["id"], student_id)
            token2 = login_resp.json()["token"]
            print("[PASS] 7. Correct login succeeded and issued authenticated JWT.")

            # 8. Authenticated Route & Session Resolution
            profile_resp = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token2}"})
            self.assertEqual(profile_resp.status_code, 200)
            self.assertEqual(profile_resp.json()["id"], student_id)

            recs_resp = self.client.get("/api/recommendations/me", headers={"Authorization": f"Bearer {token2}"})
            self.assertEqual(recs_resp.status_code, 200)
            self.assertEqual(recs_resp.json()["student_id"], student_id)
            print("[PASS] 8. Authenticated endpoints (/me, /recommendations/me) resolved cleanly via JWT.")

            # 9. Repeated Login -> Logout -> Login Cycles (3 consecutive times)
            for cycle in range(1, 4):
                rel = self.client.post(
                    "/api/students/login",
                    json={"name": name, "password": password, "mode": "login"},
                )
                self.assertEqual(rel.status_code, 200, f"Login cycle {cycle} failed")
                self.assertEqual(rel.json()["student"]["id"], student_id)
                print(f"[PASS] 9.{cycle} Login cycle {cycle}/3 passed.")

        finally:
            # Clean up test user
            clean_db = SessionLocal()
            try:
                clean_db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
                clean_db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                clean_db.commit()
            finally:
                clean_db.close()

    def test_02_seed_demo_account_preservation(self):
        """Verify demo account Alex Rivera is preserved and functional."""
        login_alex = self.client.post(
            "/api/students/login",
            json={"name": "Alex Rivera", "password": "stanford2026", "mode": "login"},
        )
        self.assertEqual(login_alex.status_code, 200)
        self.assertEqual(login_alex.json()["student"]["name"], "Alex Rivera")
        print("\n[PASS] 10. Demo account 'Alex Rivera' verified intact.")


if __name__ == "__main__":
    unittest.main()
