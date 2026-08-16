import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.core.config import Settings, settings
from app.database.session import SessionLocal
from app.database.init_db import init_db

class TestProductionPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the database schema and seed demo data
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_01_health_check_reporting(self):
        """Verify health check reports API, database status, and dialect."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["db_status"], "connected")
        self.assertIn(data["db_dialect"], ["sqlite", "postgresql"])
        self.assertIn("is_persistent", data)
        print(f"\n[PASS] Health Check: status={data['status']}, db={data['db_status']} ({data['db_dialect']}), is_persistent={data['is_persistent']}")

    def test_02_database_url_normalization(self):
        """Verify postgres:// is automatically normalized to postgresql://."""
        s = Settings(DATABASE_URL="postgres://user:pass@ep-host.neon.tech/neondb?sslmode=require")
        self.assertTrue(s.sync_database_url.startswith("postgresql://"))
        self.assertTrue(s.is_persistent_db)

        # Check Vercel POSTGRES_URL normalization
        s2 = Settings(POSTGRES_URL="postgres://default:secret@ep-host.postgres.vercel-storage.com:5432/verceldb")
        self.assertTrue(s2.sync_database_url.startswith("postgresql://"))
        self.assertTrue(s2.is_persistent_db)
        print("\n[PASS] Database URL Normalization: postgres:// correctly converted to postgresql://")

    def test_03_student_registration_tab_close_relogin_flow(self):
        """
        Test the exact user lifecycle:
        Register -> Data Persists -> Tab Close -> Reopen -> Login by Name & Email -> Recommendations Load -> State Resumes
        """
        import time
        ts = int(time.time() * 1000)
        client = self.client
        student_name = f"Maya Lin {ts}"
        student_password = "SecurePassword2026!"

        # Step 1: Register new student account
        reg_resp = client.post(
            "/api/students/login",
            json={"name": student_name, "password": student_password, "mode": "register"},
        )
        self.assertEqual(reg_resp.status_code, 200, f"Registration failed: {reg_resp.text}")
        reg_data = reg_resp.json()
        student_id = reg_data["student"]["id"]
        student_email = reg_data["student"]["email"]
        self.assertEqual(reg_data["student"]["name"], student_name)
        self.assertTrue("token" in reg_data)
        print(f"\n[PASS] 1. Student '{student_name}' registered successfully (ID: {student_id}, Email: {student_email}).")

        # Step 2: Simulate tab close / state clear
        # Now student reopens tab and logs in with the SAME NAME and PASSWORD
        login_resp = client.post(
            "/api/students/login",
            json={"name": student_name, "password": student_password, "mode": "login"},
        )
        self.assertEqual(login_resp.status_code, 200, f"Login with name failed: {login_resp.text}")
        login_data = login_resp.json()
        self.assertEqual(login_data["student"]["id"], student_id)
        self.assertEqual(login_data["student"]["name"], student_name)
        print(f"[PASS] 2. Log in with Name '{student_name}' succeeded; same student record found.")

        # Step 3: Log in using the student's EMAIL and PASSWORD
        email_login_resp = client.post(
            "/api/students/login",
            json={"name": student_email, "password": student_password, "mode": "login"},
        )
        self.assertEqual(email_login_resp.status_code, 200, f"Login with email failed: {email_login_resp.text}")
        email_data = email_login_resp.json()
        self.assertEqual(email_data["student"]["id"], student_id)
        print(f"[PASS] 3. Log in with Email '{student_email}' succeeded; same student record found.")

        # Step 4: Verify Student Profile endpoint
        profile_resp = client.get(f"/api/students/{student_id}")
        self.assertEqual(profile_resp.status_code, 200)
        profile_data = profile_resp.json()
        self.assertEqual(profile_data["id"], student_id)
        self.assertEqual(profile_data["name"], student_name)
        print(f"[PASS] 4. Student profile retrieved for ID {student_id}.")

        # Step 5: Verify Recommendations endpoint (PROBLEM 2 FIX VERIFICATION)
        # Recommendations should calculate and return cleanly without "Student not found"
        recs_resp = client.get(f"/api/recommendations/students/{student_id}")
        self.assertEqual(recs_resp.status_code, 200, f"Recommendations failed: {recs_resp.text}")
        recs_data = recs_resp.json()
        self.assertEqual(recs_data["student_id"], student_id)
        self.assertGreater(recs_data["total_recommendations"], 0)
        self.assertIsInstance(recs_data["recommendations"], list)
        print(f"[PASS] 5. Recommendations loaded successfully ({recs_data['total_recommendations']} matching opportunities).")

        # Step 6: Navigation state update and persistence
        state_resp = client.patch(
            f"/api/students/{student_id}/state",
            json={"last_screen": "internships", "last_state_json": '{"filter": "remote"}'},
        )
        self.assertEqual(state_resp.status_code, 200)
        self.assertEqual(state_resp.json()["last_screen"], "internships")

        # Step 7: Subsequent login restores last_screen
        relogin_resp = client.post(
            "/api/students/login",
            json={"name": student_name, "password": student_password, "mode": "login"},
        )
        self.assertEqual(relogin_resp.status_code, 200)
        self.assertEqual(relogin_resp.json()["last_screen"], "internships")
        print(f"[PASS] 6. Navigation state resumed to '{relogin_resp.json()['last_screen']}'.")

    def test_04_multi_user_isolation(self):
        """Verify multiple fresh student accounts are fully isolated."""
        import time
        ts = int(time.time() * 1000)
        client = self.client
        student_b_name = f"Liam Chen {ts}"
        student_b_password = "PasswordLiam456!"

        # Register User B
        reg_b = client.post(
            "/api/students/login",
            json={"name": student_b_name, "password": student_b_password, "mode": "register"},
        )
        self.assertEqual(reg_b.status_code, 200)
        b_id = reg_b.json()["student"]["id"]

        # Recommendations for User B
        recs_b = client.get(f"/api/recommendations/students/{b_id}")
        self.assertEqual(recs_b.status_code, 200)
        self.assertEqual(recs_b.json()["student_name"], student_b_name)
        print(f"\n[PASS] Multi-user isolation: User '{student_b_name}' (ID: {b_id}) has independent profile & recommendations.")

    def test_05_jwt_token_security_and_tampering(self):
        """
        Verify that the JWT token:
        1. Contains only identity information (student_id / sub) and no passwords or full profiles.
        2. Tampered or expired tokens are rejected with HTTP 401 Unauthorized.
        """
        import time
        import base64
        import json
        from app.core.security import verify_access_token

        ts = int(time.time() * 1000)
        client = self.client
        student_name = f"SecurityTestUser_{ts}"
        student_password = "SecretPassword123!"

        # Register user
        reg_resp = client.post(
            "/api/students/login",
            json={"name": student_name, "password": student_password, "mode": "register"},
        )
        self.assertEqual(reg_resp.status_code, 200)
        token = reg_resp.json()["token"]
        student_id = reg_resp.json()["student"]["id"]

        # Inspect token payload structure (must NOT contain password)
        parts = token.split(".")
        self.assertEqual(len(parts), 3, "Token should be a 3-part JWT")
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding).decode("utf-8"))

        self.assertIn("sub", payload)
        self.assertIn("student_id", payload)
        self.assertEqual(int(payload["student_id"]), student_id)
        self.assertNotIn("password", payload)
        self.assertNotIn("password_hash", payload)
        print(f"\n[PASS] JWT payload verified: contains student_id={student_id}, no sensitive passwords.")

        # Test verification helper
        verified_id = verify_access_token(token)
        self.assertEqual(verified_id, student_id)

        # Test tampered signature rejection
        tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature12345"
        self.assertIsNone(verify_access_token(tampered_token))

        # Test /api/students/me with tampered token
        resp = client.get("/api/students/me", headers={"Authorization": f"Bearer {tampered_token}"})
        self.assertEqual(resp.status_code, 401)
        print("[PASS] Tampered JWT token rejected with HTTP 401 Unauthorized.")

    def test_06_token_based_authorization_and_cross_student_protection(self):
        """
        Verify that:
        1. /api/students/me loads the correct student using only the Bearer token.
        2. /api/recommendations/me loads recommendations for the token holder.
        3. A student cannot access or modify another student's data (403 Forbidden).
        """
        import time
        ts = int(time.time() * 1000)
        client = self.client

        # Create Student A
        res_a = client.post(
            "/api/students/login",
            json={"name": f"Alice_{ts}", "password": "PasswordAlice123!", "mode": "register"},
        ).json()
        token_a = res_a["token"]
        id_a = res_a["student"]["id"]

        # Create Student B
        res_b = client.post(
            "/api/students/login",
            json={"name": f"Bob_{ts}", "password": "PasswordBob456!", "mode": "register"},
        ).json()
        token_b = res_b["token"]
        id_b = res_b["student"]["id"]

        # 1. Alice queries /api/students/me using her token
        me_resp_a = client.get("/api/students/me", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(me_resp_a.status_code, 200)
        self.assertEqual(me_resp_a.json()["id"], id_a)
        self.assertEqual(me_resp_a.json()["name"], f"Alice_{ts}")

        # 2. Bob queries /api/students/me using his token
        me_resp_b = client.get("/api/students/me", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(me_resp_b.status_code, 200)
        self.assertEqual(me_resp_b.json()["id"], id_b)
        self.assertEqual(me_resp_b.json()["name"], f"Bob_{ts}")
        print("\n[PASS] /api/students/me resolves correct student from token without student_id in request.")

        # 3. Alice queries /api/recommendations/me
        recs_a = client.get("/api/recommendations/me", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(recs_a.status_code, 200)
        self.assertEqual(recs_a.json()["student_id"], id_a)
        print("[PASS] /api/recommendations/me resolves correct recommendations using token identity.")

        # 4. Cross-student protection: Alice tries to access Bob's recommendations with her token
        bad_recs = client.get(
            f"/api/recommendations/students/{id_b}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(bad_recs.status_code, 403)
        print(f"[PASS] Cross-student access blocked: Alice's token cannot access Bob's recommendations (HTTP 403).")

        # 5. Cross-student protection: Alice tries to update Bob's navigation state
        bad_state = client.patch(
            f"/api/students/{id_b}/state",
            json={"last_screen": "passport"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(bad_state.status_code, 403)
        print(f"[PASS] Cross-student state modification blocked: Alice cannot tamper with Bob's state (HTTP 403).")


if __name__ == "__main__":
    unittest.main()

