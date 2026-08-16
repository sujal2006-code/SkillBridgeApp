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
from app.core.security import verify_access_token


class TestCompleteAuditAndIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()
        cls.client = TestClient(app)

    def test_user_a_and_user_b_complete_isolation(self):
        """
        Complete A-to-Z audit:
        1. Register User A
        2. User A submits Evidence A1 and Evidence A2
        3. Verify User A sees ONLY Evidence A1 and A2
        4. Register User B
        5. User B submits Evidence B1
        6. Verify User B sees ONLY Evidence B1 (ZERO User A data)
        7. Cross-student authorization security: User B blocked from accessing User A records
        8. User A logs in again -> sees User A records intact
        9. User B logs in again -> sees User B records intact
        """
        ts = int(time.time() * 1000)
        user_a_name = f"Student_A_{ts}"
        user_a_pwd = "PasswordA1"
        user_b_name = f"Student_B_{ts}"
        user_b_pwd = "PasswordB2"

        # 1. Register User A
        reg_a = self.client.post(
            "/api/students/login",
            json={"name": user_a_name, "password": user_a_pwd, "confirm_password": user_a_pwd, "mode": "register"},
        )
        self.assertEqual(reg_a.status_code, 200)
        user_a_id = reg_a.json()["student"]["id"]
        token_a = reg_a.json()["token"]
        self.assertEqual(reg_a.json()["student"]["name"], user_a_name)
        print(f"\n[PASS] 1. User A '{user_a_name}' registered successfully (ID: {user_a_id}).")

        # 2. User A submits 2 evidence items
        ev_a1 = self.client.post(
            "/api/evidence",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "title": "Quantum Algorithm Research",
                "description": "Implemented Shor algorithm in Qiskit.",
                "evidence_type": "project",
                "issuer": "Quantum Institute",
            },
        )
        self.assertEqual(ev_a1.status_code, 201)
        self.assertEqual(ev_a1.json()["student_id"], user_a_id)

        ev_a2 = self.client.post(
            "/api/evidence",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "title": "Kubernetes Microservices Capstone",
                "description": "Deployed cloud native FastAPI on GKE.",
                "evidence_type": "project",
                "issuer": "Cloud Academy",
            },
        )
        self.assertEqual(ev_a2.status_code, 201)
        self.assertEqual(ev_a2.json()["student_id"], user_a_id)
        print(f"[PASS] 2. User A submitted 2 evidence items; both tied to User A ID {user_a_id}.")

        # 3. Verify User A sees ONLY Evidence A1 & A2
        profile_a = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(profile_a.status_code, 200)
        data_a = profile_a.json()
        self.assertEqual(data_a["id"], user_a_id)
        self.assertEqual(data_a["name"], user_a_name)
        self.assertEqual(len(data_a["evidence"]), 2)
        ev_titles_a = [e["title"] for e in data_a["evidence"]]
        self.assertIn("Quantum Algorithm Research", ev_titles_a)
        self.assertIn("Kubernetes Microservices Capstone", ev_titles_a)
        print(f"[PASS] 3. User A profile verified: Name={data_a['name']}, EvidenceCount=2.")

        # 4. Register User B
        reg_b = self.client.post(
            "/api/students/login",
            json={"name": user_b_name, "password": user_b_pwd, "confirm_password": user_b_pwd, "mode": "register"},
        )
        self.assertEqual(reg_b.status_code, 200)
        user_b_id = reg_b.json()["student"]["id"]
        token_b = reg_b.json()["token"]
        self.assertNotEqual(user_a_id, user_b_id)
        self.assertEqual(reg_b.json()["student"]["name"], user_b_name)
        print(f"[PASS] 4. User B '{user_b_name}' registered successfully (ID: {user_b_id}).")

        # 5. User B submits Evidence B1
        ev_b1 = self.client.post(
            "/api/evidence",
            headers={"Authorization": f"Bearer {token_b}"},
            json={
                "title": "UX Design System for Fintech",
                "description": "Figma design system with WCAG AAA compliance.",
                "evidence_type": "project",
                "issuer": "Design Guild",
            },
        )
        self.assertEqual(ev_b1.status_code, 201)
        self.assertEqual(ev_b1.json()["student_id"], user_b_id)
        print(f"[PASS] 5. User B submitted 1 evidence item; tied to User B ID {user_b_id}.")

        # 6. Verify User B sees ONLY Evidence B1 (Zero User A data)
        profile_b = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(profile_b.status_code, 200)
        data_b = profile_b.json()
        self.assertEqual(data_b["id"], user_b_id)
        self.assertEqual(data_b["name"], user_b_name)
        self.assertEqual(len(data_b["evidence"]), 1)
        self.assertEqual(data_b["evidence"][0]["title"], "UX Design System for Fintech")
        self.assertNotIn("Quantum Algorithm Research", [e["title"] for e in data_b["evidence"]])
        print(f"[PASS] 6. User B isolation verified: Name={data_b['name']}, EvidenceCount=1, zero User A leakage.")

        # 7. Cross-student authorization security tests
        # User B cannot access User A's private evidence list
        cross_ev = self.client.get(f"/api/students/{user_a_id}/evidence", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(cross_ev.status_code, 403)
        # User B cannot access User A's recommendations
        cross_rec = self.client.get(f"/api/recommendations/students/{user_a_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(cross_rec.status_code, 403)
        print("[PASS] 7. Cross-student access blocked: User B token cannot read User A records (HTTP 403).")

        # 8. User A logs in again -> sees User A records intact
        login_a = self.client.post(
            "/api/students/login",
            json={"name": user_a_name, "password": user_a_pwd, "mode": "login"},
        )
        self.assertEqual(login_a.status_code, 200)
        token_a_new = login_a.json()["token"]
        profile_a_re = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_a_new}"})
        self.assertEqual(profile_a_re.status_code, 200)
        self.assertEqual(profile_a_re.json()["name"], user_a_name)
        self.assertEqual(len(profile_a_re.json()["evidence"]), 2)
        print(f"[PASS] 8. User A relogin verified: Name={user_a_name}, EvidenceCount=2.")

        # 9. User B logs in again -> sees User B records intact
        login_b = self.client.post(
            "/api/students/login",
            json={"name": user_b_name, "password": user_b_pwd, "mode": "login"},
        )
        self.assertEqual(login_b.status_code, 200)
        token_b_new = login_b.json()["token"]
        profile_b_re = self.client.get("/api/students/me", headers={"Authorization": f"Bearer {token_b_new}"})
        self.assertEqual(profile_b_re.status_code, 200)
        self.assertEqual(profile_b_re.json()["name"], user_b_name)
        self.assertEqual(len(profile_b_re.json()["evidence"]), 1)
        print(f"[PASS] 9. User B relogin verified: Name={user_b_name}, EvidenceCount=1.")

        # Cleanup test users
        clean_db = SessionLocal()
        try:
            clean_db.query(Activity).filter(Activity.student_id.in_([user_a_id, user_b_id])).delete(synchronize_session=False)
            clean_db.query(Evidence).filter(Evidence.student_id.in_([user_a_id, user_b_id])).delete(synchronize_session=False)
            clean_db.query(Student).filter(Student.id.in_([user_a_id, user_b_id])).delete(synchronize_session=False)
            clean_db.commit()
        finally:
            clean_db.close()


if __name__ == "__main__":
    unittest.main()
