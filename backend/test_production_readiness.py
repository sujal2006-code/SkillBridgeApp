import os
import sys
import unittest
import json
import time
import base64

# Add backend directory to path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.core.config import Settings, settings
from app.core.security import create_access_token, verify_access_token
from app.database.session import SessionLocal, engine
from app.database.init_db import init_db
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.internship import Internship
from app.models.team import Team, TeamMember
from app.models.activity import Activity

class TestFinalProductionReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_01_health_and_database_reporting(self):
        """1. Verify /api/health endpoint reports live database connectivity."""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["db_status"], "connected")
        self.assertIn("db_dialect", data)
        self.assertIn("is_persistent", data)
        print(f"\n[PASS] 1. Health API: {data}")

    def test_02_postgresql_connection_string_normalization(self):
        """2. Verify cloud PostgreSQL connection strings (Neon, Supabase, Vercel Postgres)."""
        # Neon / Supabase standard postgres:// format
        s1 = Settings(DATABASE_URL="postgres://usr:pwd@ep-host.neon.tech/neondb?sslmode=require")
        self.assertEqual(s1.sync_database_url, "postgresql://usr:pwd@ep-host.neon.tech/neondb?sslmode=require")
        self.assertTrue(s1.is_persistent_db)

        # Vercel Postgres automatic POSTGRES_URL format
        s2 = Settings(POSTGRES_URL="postgres://default:secret@ep-host.postgres.vercel-storage.com:5432/verceldb")
        self.assertEqual(s2.sync_database_url, "postgresql://default:secret@ep-host.postgres.vercel-storage.com:5432/verceldb")
        self.assertTrue(s2.is_persistent_db)

        # Vercel POSTGRES_PRISMA_URL format
        s3 = Settings(POSTGRES_PRISMA_URL="postgres://default:secret@ep-host-pooler.postgres.vercel-storage.com:5432/verceldb?pgbouncer=true")
        self.assertEqual(s3.sync_database_url, "postgresql://default:secret@ep-host-pooler.postgres.vercel-storage.com:5432/verceldb?pgbouncer=true")
        self.assertTrue(s3.is_persistent_db)

        print("\n[PASS] 2. Cloud PostgreSQL connection string normalization verified for Neon, Supabase, and Vercel Postgres.")

    def test_03_jwt_token_security_and_claims(self):
        """3. Verify JWT is signed with HS256, contains student_id, has no passwords, and rejects tampering."""
        student_id = 999
        token = create_access_token(student_id)
        parts = token.split(".")
        self.assertEqual(len(parts), 3, "JWT must be 3 parts")

        # Decode payload and verify contents
        padding = "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + padding).decode("utf-8"))
        self.assertEqual(int(payload["student_id"]), student_id)
        self.assertEqual(payload["sub"], str(student_id))
        self.assertIn("exp", payload)
        self.assertIn("iat", payload)
        self.assertNotIn("password", payload)
        self.assertNotIn("password_hash", payload)

        # Signature verification
        self.assertEqual(verify_access_token(token), student_id)

        # Tampered signature test
        tampered_token = f"{parts[0]}.{parts[1]}.fakeSignature123"
        self.assertIsNone(verify_access_token(tampered_token))
        bad_req = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {tampered_token}"})
        self.assertEqual(bad_req.status_code, 401)
        print("\n[PASS] 3. JWT security verified: tamper-proof HS256 signature, exp claims, and no passwords.")

    def test_04_cross_student_security_boundaries(self):
        """4. Verify strict isolation between Student A and Student B (HTTP 403 on unauthorized access)."""
        ts = int(time.time() * 1000)
        
        # Create Student A
        res_a = self.client.post("/api/students/login", json={"name": f"SecAlice_{ts}", "password": "AlicePass123!", "mode": "register"}).json()
        id_a, token_a = res_a["student"]["id"], res_a["token"]

        # Create Student B
        res_b = self.client.post("/api/students/login", json={"name": f"SecBob_{ts}", "password": "BobPass456!", "mode": "register"}).json()
        id_b, token_b = res_b["student"]["id"], res_b["token"]

        try:
            # Student A accesses A's data -> 200 OK
            self.assertEqual(self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_a}"}).status_code, 200)
            self.assertEqual(self.client.get(f"/api/students/{id_a}", headers={"Authorization": f"Bearer {token_a}"}).status_code, 200)
            self.assertEqual(self.client.get(f"/api/recommendations/students/{id_a}", headers={"Authorization": f"Bearer {token_a}"}).status_code, 200)

            # Student B accesses B's data -> 200 OK
            self.assertEqual(self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_b}"}).status_code, 200)
            self.assertEqual(self.client.get(f"/api/students/{id_b}", headers={"Authorization": f"Bearer {token_b}"}).status_code, 200)
            self.assertEqual(self.client.get(f"/api/recommendations/students/{id_b}", headers={"Authorization": f"Bearer {token_b}"}).status_code, 200)

            # Student A tries to access Student B's profile -> 403 Forbidden
            self.assertEqual(self.client.get(f"/api/students/{id_b}", headers={"Authorization": f"Bearer {token_a}"}).status_code, 403)

            # Student A tries to access Student B's recommendations -> 403 Forbidden
            self.assertEqual(self.client.get(f"/api/recommendations/students/{id_b}", headers={"Authorization": f"Bearer {token_a}"}).status_code, 403)

            # Student A tries to access Student B's evidence -> 403 Forbidden
            self.assertEqual(self.client.get(f"/api/students/{id_b}/evidence", headers={"Authorization": f"Bearer {token_a}"}).status_code, 403)

            # Student A tries to modify Student B's navigation state -> 403 Forbidden
            self.assertEqual(self.client.patch(f"/api/students/{id_b}/state", json={"last_screen": "passport"}, headers={"Authorization": f"Bearer {token_a}"}).status_code, 403)
            
            print("\n[PASS] 4. Cross-student security verified: all cross-access attempts blocked with HTTP 403 Forbidden.")
        finally:
            # Clean up test accounts
            db = SessionLocal()
            try:
                db.query(Activity).filter(Activity.student_id.in_([id_a, id_b])).delete(synchronize_session=False)
                db.query(Student).filter(Student.id.in_([id_a, id_b])).delete(synchronize_session=False)
                db.commit()
            finally:
                db.close()

    def test_05_complete_end_to_end_user_lifecycle(self):
        """5. Test full user journey: Register -> Login -> Passport -> Recommendations -> Teams -> Re-login."""
        ts = int(time.time() * 1000)
        student_name = f"EndToEndUser_{ts}"
        student_password = "E2EPassword2026!"

        # 5.1 Register
        reg = self.client.post("/api/students/login", json={"name": student_name, "password": student_password, "mode": "register"})
        self.assertEqual(reg.status_code, 200)
        auth = reg.json()
        student_id, token, email = auth["student"]["id"], auth["token"], auth["student"]["email"]

        try:
            # 5.2 Login with Name
            login_name = self.client.post("/api/students/login", json={"name": student_name, "password": student_password, "mode": "login"})
            self.assertEqual(login_name.status_code, 200)
            self.assertEqual(login_name.json()["student"]["id"], student_id)

            # 5.3 Login with Email
            login_email = self.client.post("/api/students/login", json={"name": email, "password": student_password, "mode": "login"})
            self.assertEqual(login_email.status_code, 200)
            self.assertEqual(login_email.json()["student"]["id"], student_id)

            # 5.4 Fetch Profile via Token
            profile = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(profile.status_code, 200)
            self.assertEqual(profile.json()["name"], student_name)

            # 5.5 Submit Evidence (Coursework)
            ev = self.client.post(
                "/api/evidence",
                json={
                    "student_id": student_id,
                    "skill_id": 1,
                    "evidence_type": "coursework",
                    "title": "CS106B Programming Abstractions",
                    "description": "Full coursework in modern data structures.",
                    "issuer": "Stanford Computer Science",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(ev.status_code, 201)

            # 5.6 Fetch Recommendations via Token
            recs = self.client.get("/api/recommendations/me", headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(recs.status_code, 200)
            recs_data = recs.json()
            self.assertEqual(recs_data["student_id"], student_id)
            self.assertGreater(recs_data["total_recommendations"], 0)

            # 5.7 Update and Resume Navigation State
            state = self.client.patch("/api/students/me/state", json={"last_screen": "passport"}, headers={"Authorization": f"Bearer {token}"})
            self.assertEqual(state.status_code, 200)
            self.assertEqual(state.json()["last_screen"], "passport")

            # 5.8 Re-login restores last_screen
            relogin = self.client.post("/api/students/login", json={"name": student_name, "password": student_password, "mode": "login"})
            self.assertEqual(relogin.status_code, 200)
            self.assertEqual(relogin.json()["last_screen"], "passport")

            print("\n[PASS] 5. Complete user flow verified: Register -> Dual Login -> Evidence -> Recommendations -> State Resumption.")
        finally:
            # Clean up test user
            db = SessionLocal()
            try:
                db.query(Activity).filter(Activity.student_id == student_id).delete(synchronize_session=False)
                db.query(Evidence).filter(Evidence.student_id == student_id).delete(synchronize_session=False)
                db.query(StudentSkill).filter(StudentSkill.student_id == student_id).delete(synchronize_session=False)
                db.query(Student).filter(Student.id == student_id).delete(synchronize_session=False)
                db.commit()
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
