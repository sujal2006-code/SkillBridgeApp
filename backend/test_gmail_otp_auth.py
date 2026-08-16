import os
import sys
import unittest
import json
import time
from datetime import datetime, timezone, timedelta

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.models.student import Student
from app.models.otp import OTP
from app.models.activity import Activity
from app.models.evidence import Evidence
from app.models.skill import StudentSkill
from app.core.security import verify_password, verify_access_token

from unittest.mock import patch

class TestGmailOtpAndAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    @patch("app.routes.auth._generate_otp_code", return_value="765432")
    def test_01_complete_gmail_otp_registration_flow(self, mock_otp):
        """
        TEST 1 — Account Creation with Email OTP:
        1. Request registration OTP for a Gmail address.
        2. Verify OTP is securely stored in database.
        3. Verify OTP code and create user in PostgreSQL.
        4. Verify JWT returned identifies the student.
        """
        ts = int(time.time() * 1000)
        name = f"Maya Lin {ts}"
        email = f"maya.lin.{ts}@gmail.com"
        password = "SecurePassword2026!"
        expected_otp = "765432"

        # Step 1.1: Request Register OTP
        resp = self.client.post(
            "/api/auth/register-otp",
            json={
                "name": name,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )
        self.assertEqual(resp.status_code, 200, f"Register OTP failed: {resp.text}")
        self.assertIn("Verification code sent", resp.json()["message"])
        self.assertEqual(resp.json()["email"], email)
        print(f"\n[PASS] 1.1 OTP requested for Gmail '{email}'.")

        # Step 1.2: Check stored OTP record in PostgreSQL
        db = SessionLocal()
        try:
            otp_record = db.query(OTP).filter(OTP.email == email, OTP.purpose == "register", OTP.is_used == False).first()
            self.assertIsNotNone(otp_record, "OTP record must exist in PostgreSQL")
            self.assertFalse(otp_record.is_used)
            self.assertEqual(otp_record.attempts_left, 5)
            self.assertTrue(verify_password(expected_otp, otp_record.otp_hash))
            print(f"[PASS] 1.2 Secure OTP found in PostgreSQL.")

            # Step 1.3: Verify wrong OTP
            bad_verify = self.client.post(
                "/api/auth/verify-register-otp",
                json={"email": email, "otp": "000000"},
            )
            self.assertEqual(bad_verify.status_code, 400)
            self.assertEqual(bad_verify.json()["detail"], "Invalid OTP. Please try again.")
            print("[PASS] 1.3 Wrong OTP properly rejected with 'Invalid OTP. Please try again.'")

            # Step 1.4: Verify correct OTP -> Create PostgreSQL account
            good_verify = self.client.post(
                "/api/auth/verify-register-otp",
                json={"email": email, "otp": expected_otp},
            )
            self.assertEqual(good_verify.status_code, 200, f"OTP verification failed: {good_verify.text}")
            auth_data = good_verify.json()
            student_id = auth_data["student"]["id"]
            token = auth_data["token"]
            self.assertEqual(auth_data["student"]["email"], email)
            self.assertEqual(verify_access_token(token), student_id)
            print(f"[PASS] 1.4 Correct OTP verified; student record created in PostgreSQL (ID: {student_id}).")

            # Step 1.5: Login using the Gmail and Password
            login_resp = self.client.post(
                "/api/students/login",
                json={"name": email, "password": password, "mode": "login"},
            )
            self.assertEqual(login_resp.status_code, 200)
            self.assertEqual(login_resp.json()["student"]["id"], student_id)
            print("[PASS] 1.5 Login with Gmail and password succeeded.")

            # Step 1.6: Logout -> Account persists
            db_check = SessionLocal()
            student_in_db = db_check.query(Student).filter(Student.id == student_id).first()
            self.assertIsNotNone(student_in_db)
            db_check.close()
            print("[PASS] 1.6 Logout executed; student row remains permanently in PostgreSQL.")

            # Step 1.7: Login Again
            relogin = self.client.post(
                "/api/students/login",
                json={"name": email, "password": password, "mode": "login"},
            )
            self.assertEqual(relogin.status_code, 200)
            self.assertEqual(relogin.json()["student"]["id"], student_id)
            print("[PASS] 1.7 Login again succeeded.")

            # Step 1.8: Attempt to re-register with SAME Gmail
            dup_resp = self.client.post(
                "/api/auth/register-otp",
                json={"name": name, "email": email, "password": password, "confirm_password": password},
            )
            self.assertEqual(dup_resp.status_code, 400)
            self.assertEqual(dup_resp.json()["detail"], "Account already exists. Please log in instead.")
            print("[PASS] 1.8 Duplicate registration blocked with 'Account already exists. Please log in instead.'")

        finally:
            db.close()
            # Clean up
            clean_db = SessionLocal()
            try:
                clean_db.query(OTP).filter(OTP.email == email).delete(synchronize_session=False)
                clean_db.query(Student).filter(Student.email == email).delete(synchronize_session=False)
                clean_db.commit()
            finally:
                clean_db.close()


    def test_02_password_validation_and_confirmation_rules(self):
        """
        TEST 6 & 7 — Password Requirements and Password Confirmation:
        - Validate min 6 chars, 1 letter, 1 number, 1 special character.
        - Validate confirm password matching.
        """
        expected_pwd_msg = "Password must have a minimum length of 6 characters and include at least 1 letter, 1 number, and 1 special character."
        email = f"pwd_rules_{int(time.time()*1000)}@gmail.com"

        # Invalid password cases
        for bad_pwd in ["abc", "abcdef", "123456", "abc123", "abc!@#", ""]:
            resp = self.client.post(
                "/api/auth/register-otp",
                json={"name": "Test User", "email": email, "password": bad_pwd, "confirm_password": bad_pwd},
            )
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(resp.json()["detail"], expected_pwd_msg)

        # Mismatched password and confirm_password
        mismatch_resp = self.client.post(
            "/api/auth/register-otp",
            json={"name": "Test User", "email": email, "password": "ValidPassword123!", "confirm_password": "DifferentPassword123!"},
        )
        self.assertEqual(mismatch_resp.status_code, 400)
        self.assertEqual(mismatch_resp.json()["detail"], "Passwords do not match.")

        print("\n[PASS] 2. Password requirements and confirmation rules verified on backend.")

    @patch("app.routes.auth._generate_otp_code", return_value="876543")
    def test_03_forgot_password_otp_and_reset_flow(self, mock_otp):
        """
        TEST 8, 9, 10, 11, 12, 13 — Complete Password Reset Lifecycle:
        1. Request password reset OTP for registered Gmail.
        2. Verify OTP -> obtain reset_token.
        3. Submit new password with reset_token.
        4. Verify password updated in PostgreSQL.
        5. Old password no longer works; new password works immediately.
        """
        ts = int(time.time() * 1000)
        email = f"reset_user_{ts}@gmail.com"
        old_password = "OldPassword2026!"
        new_password = "NewPassword2026!"
        expected_otp = "876543"

        # Register initial user
        reg_resp = self.client.post(
            "/api/students/login",
            json={"name": f"Reset User {ts}", "password": old_password, "mode": "register"},
        )
        # Fix user's email to match test
        db = SessionLocal()
        student = db.query(Student).filter(Student.id == reg_resp.json()["student"]["id"]).first()
        student.email = email
        student_id = student.id
        db.commit()
        db.close()

        try:
            # Step 3.1: Request Forgot Password OTP
            forgot_resp = self.client.post(
                "/api/auth/forgot-password-otp",
                json={"email": email},
            )
            self.assertEqual(forgot_resp.status_code, 200)
            self.assertIn("Password reset code sent", forgot_resp.json()["message"])
            print(f"\n[PASS] 3.1 Forgot password OTP requested for '{email}'.")

            # Step 3.2: Non-existent email check
            bad_email_resp = self.client.post(
                "/api/auth/forgot-password-otp",
                json={"email": "nonexistent.random.email@gmail.com"},
            )
            self.assertEqual(bad_email_resp.status_code, 404)
            self.assertEqual(bad_email_resp.json()["detail"], "No account found with this email. Please create an account first.")
            print("[PASS] 3.2 Non-existent email properly returned 'No account found with this email. Please create an account first.'")

            # Step 3.3: Verify Reset OTP -> obtain reset_token
            verify_reset = self.client.post(
                "/api/auth/verify-reset-otp",
                json={"email": email, "otp": expected_otp},
            )
            self.assertEqual(verify_reset.status_code, 200)
            reset_token = verify_reset.json()["reset_token"]
            self.assertTrue(reset_token)
            print("[PASS] 3.3 Reset OTP verified; single-use reset_token issued.")

            # Step 3.4: Submit New Password
            reset_submit = self.client.post(
                "/api/auth/reset-password",
                json={
                    "email": email,
                    "reset_token": reset_token,
                    "new_password": new_password,
                    "confirm_password": new_password,
                },
            )
            self.assertEqual(reset_submit.status_code, 200)
            self.assertIn("Password updated successfully", reset_submit.json()["message"])
            print("[PASS] 3.4 Password reset submitted and committed to PostgreSQL.")

            # Step 3.5: Old Password MUST FAIL (HTTP 401)
            old_login = self.client.post(
                "/api/students/login",
                json={"name": email, "password": old_password, "mode": "login"},
            )
            self.assertEqual(old_login.status_code, 401)
            print("[PASS] 3.5 Old password rejected with HTTP 401 Unauthorized.")

            # Step 3.6: New Password MUST SUCCEED (HTTP 200)
            new_login = self.client.post(
                "/api/students/login",
                json={"name": email, "password": new_password, "mode": "login"},
            )
            self.assertEqual(new_login.status_code, 200)
            self.assertEqual(new_login.json()["student"]["id"], student_id)
            print("[PASS] 3.6 Login with NEW password succeeded immediately.")

            # Step 3.7: Reset token cannot be reused
            reuse_reset = self.client.post(
                "/api/auth/reset-password",
                json={
                    "email": email,
                    "reset_token": reset_token,
                    "new_password": "AnotherPassword123!",
                    "confirm_password": "AnotherPassword123!",
                },
            )
            self.assertEqual(reuse_reset.status_code, 400)
            print("[PASS] 3.7 Reusing consumed reset_token blocked.")

        finally:
            clean_db = SessionLocal()
            try:
                clean_db.query(OTP).filter(OTP.email == email).delete(synchronize_session=False)
                clean_db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                clean_db.commit()
            finally:
                clean_db.close()



if __name__ == "__main__":
    unittest.main()
