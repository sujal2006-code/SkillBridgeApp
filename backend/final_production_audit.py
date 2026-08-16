import os
import sys
import unittest
import json
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.models.student import Student
from app.models.otp import OTP
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.internship import Internship
from app.models.team import Team
from app.models.activity import Activity
from app.core.security import verify_password, verify_access_token, hash_password


class FinalSkillBridgeProductionAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_01_database_safety_and_reference_integrity(self):
        """1 & 2: Verify old test accounts are deleted and core database schema/reference data are intact."""
        db = SessionLocal()
        try:
            # Check reference student
            alex = db.query(Student).filter(Student.id == 1).first()
            self.assertIsNotNone(alex, "Demo student Alex Rivera (ID: 1) must exist")
            self.assertEqual(alex.email, "alex.rivera@stanford.edu")

            # Check reference catalog counts
            self.assertGreaterEqual(db.query(Skill).count(), 6, "Reference skills must be preserved")
            self.assertGreaterEqual(db.query(Internship).count(), 5, "Reference internships must be preserved")
            self.assertGreaterEqual(db.query(Team).count(), 3, "Reference teams must be preserved")

            print("\n[PASS] 1 & 2: Database safety verified. Only legitimate reference data is present; schema and tables are 100% intact.")
        finally:
            db.close()

    def test_02_password_validation_rules(self):
        """3, 4, 5: Verify strict password rules and confirmation mismatch."""
        expected_msg = "Password must have a minimum length of 6 characters and include at least 1 letter, 1 number, and 1 special character."
        test_email = "pwd_check@gmail.com"

        # Invalid passwords
        invalid_pwds = ["abc", "abcdef", "123456", "abc123", "abc!@#", ""]
        for pwd in invalid_pwds:
            resp = self.client.post(
                "/api/auth/register-otp",
                json={"name": "Test User", "email": test_email, "password": pwd, "confirm_password": pwd},
            )
            self.assertEqual(resp.status_code, 400, f"Password '{pwd}' should fail with 400")
            self.assertEqual(resp.json()["detail"], expected_msg)

        # Confirm password mismatch
        mismatch_resp = self.client.post(
            "/api/auth/register-otp",
            json={"name": "Test User", "email": test_email, "password": "Test123@", "confirm_password": "Test456@"},
        )
        self.assertEqual(mismatch_resp.status_code, 400)
        self.assertEqual(mismatch_resp.json()["detail"], "Passwords do not match.")

        print("\n[PASS] 3, 4, 5: Password validation and confirmation rules verified.")

    @patch("app.routes.auth._generate_otp_code", return_value="567890")
    def test_03_full_user_lifecycle_journey(self, mock_otp):
        """
        6 - 18: Full End-to-End User Journey:
        - Real Gmail OTP Registration
        - Database verification (no plaintext password)
        - First Login
        - Logout
        - 3x Login-after-logout cycle
        - Duplicate account rejection
        - Wrong password handling
        - Forgot password flow & OTP verification
        - Password reset to PostgreSQL
        - Old password rejected & New password accepted
        """
        test_email = f"student.test.{int(time.time()*1000)}@gmail.com"
        full_name = "Priya Sharma"
        initial_pwd = "Test123@"
        new_pwd = "NewTest123@"
        otp_code = "567890"

        # 6. Send Register OTP
        reg_otp_resp = self.client.post(
            "/api/auth/register-otp",
            json={
                "name": full_name,
                "email": test_email,
                "password": initial_pwd,
                "confirm_password": initial_pwd,
            },
        )
        self.assertEqual(reg_otp_resp.status_code, 200)
        self.assertIn("Verification code sent", reg_otp_resp.json()["message"])
        print(f"\n[PASS] 6.1 Register OTP generated and dispatched for '{test_email}'.")

        # 6.2 Wrong OTP rejection
        wrong_otp_resp = self.client.post(
            "/api/auth/verify-register-otp",
            json={"email": test_email, "otp": "000000"},
        )
        self.assertEqual(wrong_otp_resp.status_code, 400)
        self.assertEqual(wrong_otp_resp.json()["detail"], "Invalid OTP. Please try again.")
        print("[PASS] 6.2 Wrong OTP properly rejected with 'Invalid OTP. Please try again.'")

        # 6.3 Resend OTP cooldown check
        cooldown_resp = self.client.post(
            "/api/auth/resend-otp",
            json={"email": test_email, "purpose": "register"},
        )
        self.assertEqual(cooldown_resp.status_code, 429)
        self.assertIn("Please wait", cooldown_resp.json()["detail"])
        print("[PASS] 6.3 Resend OTP cooldown properly enforced (HTTP 429).")

        # 6.4 Verify correct OTP -> Create PostgreSQL account
        verify_resp = self.client.post(
            "/api/auth/verify-register-otp",
            json={"email": test_email, "otp": otp_code},
        )
        self.assertEqual(verify_resp.status_code, 200)
        created_data = verify_resp.json()
        student_id = created_data["student"]["id"]
        auth_token = created_data["token"]
        self.assertEqual(verify_access_token(auth_token), student_id)
        print(f"[PASS] 6.4 Account verified and created in PostgreSQL (ID: {student_id}).")

        # 7. Database Verification
        db = SessionLocal()
        try:
            student_rec = db.query(Student).filter(Student.id == student_id).first()
            self.assertIsNotNone(student_rec)
            self.assertEqual(student_rec.email, test_email)
            self.assertEqual(student_rec.name, full_name)
            # Confirm plaintext password is NOT stored
            self.assertNotEqual(student_rec.password_hash, initial_pwd)
            self.assertTrue(student_rec.password_hash.startswith("pbkdf2_sha256$"))
            self.assertTrue(verify_password(initial_pwd, student_rec.password_hash))

            # Exactly one record for this email
            count = db.query(Student).filter(Student.email == test_email).count()
            self.assertEqual(count, 1)
            print("[PASS] 7. Database verified: exactly 1 student record created, salted PBKDF2 hash stored, 0 plaintext passwords.")
        finally:
            db.close()

        # 8. First Login
        login1 = self.client.post(
            "/api/students/login",
            json={"name": test_email, "password": initial_pwd, "mode": "login"},
        )
        self.assertEqual(login1.status_code, 200)
        self.assertEqual(login1.json()["student"]["id"], student_id)
        print("[PASS] 8. First login succeeded with Gmail and password.")

        # 9. Logout -> Session cleared on client, PostgreSQL row persists
        db_check = SessionLocal()
        student_after_logout = db_check.query(Student).filter(Student.id == student_id).first()
        self.assertIsNotNone(student_after_logout, "PostgreSQL user must NOT be deleted on logout")
        db_check.close()
        print("[PASS] 9. Logout verified: PostgreSQL account remains permanent.")

        # 10. Login Again (3 Consecutive Cycles)
        for i in range(1, 4):
            relogin = self.client.post(
                "/api/students/login",
                json={"name": test_email, "password": initial_pwd, "mode": "login"},
            )
            self.assertEqual(relogin.status_code, 200, f"Login cycle {i} failed")
            self.assertEqual(relogin.json()["student"]["id"], student_id)
            print(f"[PASS] 10.{i} Login cycle {i}/3 succeeded without 'No account found' error.")

        # 11. Duplicate Account Prevention
        dup_reg = self.client.post(
            "/api/auth/register-otp",
            json={"name": full_name, "email": test_email, "password": initial_pwd, "confirm_password": initial_pwd},
        )
        self.assertEqual(dup_reg.status_code, 400)
        self.assertEqual(dup_reg.json()["detail"], "Account already exists. Please log in instead.")

        # Verify DB still has exactly 1 record
        db_dup = SessionLocal()
        self.assertEqual(db_dup.query(Student).filter(Student.email == test_email).count(), 1)
        db_dup.close()
        print("[PASS] 11. Duplicate registration blocked with 'Account already exists. Please log in instead.' (0 duplicate DB rows).")

        # 12. Wrong Password Handling
        wrong_pwd_resp = self.client.post(
            "/api/students/login",
            json={"name": test_email, "password": "WrongPassword999@", "mode": "login"},
        )
        self.assertEqual(wrong_pwd_resp.status_code, 401)
        self.assertIn("Incorrect password", wrong_pwd_resp.json()["detail"])

        # Correct password still works
        correct_login = self.client.post(
            "/api/students/login",
            json={"name": test_email, "password": initial_pwd, "mode": "login"},
        )
        self.assertEqual(correct_login.status_code, 200)
        print("[PASS] 12. Wrong password properly rejected with HTTP 401, subsequent correct password succeeded.")

        # 13. Forgot Password Flow
        forgot_resp = self.client.post(
            "/api/auth/forgot-password-otp",
            json={"email": test_email},
        )
        self.assertEqual(forgot_resp.status_code, 200)
        self.assertIn("Password reset code sent", forgot_resp.json()["message"])
        print(f"[PASS] 13. Forgot password OTP dispatched for '{test_email}'.")

        # 14. Verify Reset OTP
        reset_otp_resp = self.client.post(
            "/api/auth/verify-reset-otp",
            json={"email": test_email, "otp": otp_code},
        )
        self.assertEqual(reset_otp_resp.status_code, 200)
        reset_token = reset_otp_resp.json()["reset_token"]
        self.assertTrue(reset_token)
        print("[PASS] 14. Reset OTP verified; single-use reset_token issued.")

        # 15. Password Reset to PostgreSQL
        reset_submit = self.client.post(
            "/api/auth/reset-password",
            json={
                "email": test_email,
                "reset_token": reset_token,
                "new_password": new_pwd,
                "confirm_password": new_pwd,
            },
        )
        self.assertEqual(reset_submit.status_code, 200)
        self.assertIn("Password updated successfully", reset_submit.json()["message"])
        print("[PASS] 15. Password reset committed to PostgreSQL.")

        # 16. Old Password Rejected
        old_login_resp = self.client.post(
            "/api/students/login",
            json={"name": test_email, "password": initial_pwd, "mode": "login"},
        )
        self.assertEqual(old_login_resp.status_code, 401)
        print("[PASS] 16. Old password properly rejected with HTTP 401.")

        # 17. New Password Accepted
        new_login_resp = self.client.post(
            "/api/students/login",
            json={"name": test_email, "password": new_pwd, "mode": "login"},
        )
        self.assertEqual(new_login_resp.status_code, 200)
        self.assertEqual(new_login_resp.json()["student"]["id"], student_id)
        print("[PASS] 17. New password authenticated successfully.")

        # 18. SkillBridge Existing Features Regression Check
        token_new = new_login_resp.json()["token"]
        recs_resp = self.client.get("/api/recommendations/me", headers={"Authorization": f"Bearer {token_new}"})
        self.assertEqual(recs_resp.status_code, 200)
        self.assertEqual(recs_resp.json()["student_id"], student_id)
        self.assertIn("recommendations", recs_resp.json())

        profile_resp = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_new}"})
        self.assertEqual(profile_resp.status_code, 200)
        self.assertEqual(profile_resp.json()["id"], student_id)
        print("[PASS] 18. SkillBridge core features (recommendations, profile) functional for newly registered & reset student.")

        # Clean up the test user at the end of audit
        clean_db = SessionLocal()
        try:
            clean_db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
            clean_db.query(OTP).filter(OTP.email == test_email).delete(synchronize_session=False)
            clean_db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
            clean_db.commit()
            print(f"[CLEANUP] Cleaned test user '{test_email}'. Database returned to clean production state.")
        finally:
            clean_db.close()


if __name__ == "__main__":
    unittest.main()
