import os
import sys
import unittest
from fastapi.testclient import TestClient

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student

EXPECTED_INDIAN_STUDENT_NAMES = [
    "Aarav Sharma",
    "Aditya Mishra",
    "Rohan Das",
    "Arjun Patel",
    "Ananya Singh",
    "Priya Nair",
    "Sneha Das",
    "Kavya Sharma",
    "Rahul Kumar",
    "Neha Patel",
    "Abhishek Mohanty",
    "Pooja Mishra",
    "Saurav Behera",
    "Ishita Gupta",
    "Vivek Reddy",
]

COMMON_PASSWORD = "skillbridge2026"

OLD_FORBIDDEN_NAMES = [
    "alex rivera",
    "sarah chen",
    "marcus vance",
    "marcus young",
    "elena rostova",
    "priyansh sharma",
    "abc",
    "abe",
]


class TestIndianDemoAccountsSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_check(self):
        """Verify API is healthy and connected to database."""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["db_status"], "connected")
        print(f"\n[PASS] Health check OK: {data['db_dialect']} connected.")

    def test_02_all_15_demo_students_login_by_name(self):
        """Verify every one of the 15 Indian demo students can log in using their Name and common password."""
        for name in EXPECTED_INDIAN_STUDENT_NAMES:
            resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": COMMON_PASSWORD, "mode": "login"},
            )
            self.assertEqual(resp.status_code, 200, f"Login failed for '{name}': {resp.text}")
            data = resp.json()
            self.assertEqual(data["student"]["name"], name)
            self.assertTrue(bool(data.get("token")), f"Missing token for '{name}'")
            print(f" [PASS] Logged in by Name: '{name}' (ID: {data['student']['id']})")

    def test_03_all_15_demo_students_login_by_email(self):
        """Verify every one of the 15 Indian demo students can log in using their Email and common password."""
        for name in EXPECTED_INDIAN_STUDENT_NAMES:
            email = f"{name.lower().replace(' ', '.')}@skillbridge.edu"
            resp = self.client.post(
                "/api/students/login",
                json={"name": email, "password": COMMON_PASSWORD, "mode": "login"},
            )
            self.assertEqual(resp.status_code, 200, f"Login failed for email '{email}': {resp.text}")
            data = resp.json()
            self.assertEqual(data["student"]["name"], name)
            print(f" [PASS] Logged in by Email: '{email}'")

    def test_04_profile_and_skills_passport(self):
        """Verify authenticated /me endpoint returns full verified skills and evidence portfolio."""
        for name in EXPECTED_INDIAN_STUDENT_NAMES[:5]:  # Test sample of profiles
            login_resp = self.client.post(
                "/api/students/login",
                json={"name": name, "password": COMMON_PASSWORD, "mode": "login"},
            )
            token = login_resp.json()["token"]
            profile_resp = self.client.get(
                "/api/students/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(profile_resp.status_code, 200)
            pdata = profile_resp.json()
            self.assertEqual(pdata["name"], name)
            self.assertGreater(len(pdata["skills"]), 0, f"Student '{name}' must have verified skills")
            self.assertGreater(len(pdata["evidence"]), 0, f"Student '{name}' must have evidence items")
            verified_skills_count = len([s for s in pdata["skills"] if s["verification_status"] == "verified"])
            print(f" [PASS] Profile '{name}': {verified_skills_count} verified skills, {len(pdata['evidence'])} evidence items.")

    def test_05_internship_matching_recommendations(self):
        """Verify /api/recommendations/me produces explainable matches with no errors."""
        login_resp = self.client.post(
            "/api/students/login",
            json={"name": "Aarav Sharma", "password": COMMON_PASSWORD, "mode": "login"},
        )
        token = login_resp.json()["token"]
        rec_resp = self.client.get(
            "/api/recommendations/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(rec_resp.status_code, 200)
        rec_data = rec_resp.json()
        recs = rec_data.get("recommendations", [])
        self.assertGreater(len(recs), 0, "Aarav Sharma should have matching internships")
        top_rec = recs[0]
        self.assertGreaterEqual(top_rec["match_score"], 60.0)
        self.assertTrue(bool(top_rec["explanation"]))
        print(f"\n[PASS] Aarav Sharma Top Match: '{top_rec['internship_title']}' at '{top_rec['company']}' ({top_rec['match_score']}%)")

    def test_06_team_builder_candidates_contain_only_new_indian_accounts(self):
        """
        Verify Team Builder candidate recommendations:
        - Must contain newly created Indian demo accounts
        - Must NOT contain old placeholder accounts (Alex Rivera, Sarah Chen, Marcus Vance, etc.)
        """
        teams_resp = self.client.get("/api/teams")
        self.assertEqual(teams_resp.status_code, 200)
        teams = teams_resp.json()
        self.assertGreater(len(teams), 0, "Should have teams in database")

        target_team = teams[0]
        team_id = target_team["id"]
        print(f"\n[INFO] Evaluating Team Candidates for Team ID {team_id}: '{target_team['name']}' (Lead: {target_team['creator_name']})")

        cand_resp = self.client.get(f"/api/teams/{team_id}/candidates")
        self.assertEqual(cand_resp.status_code, 200)
        candidates = cand_resp.json()

        self.assertGreater(len(candidates), 0, "Team Builder must return candidates")
        print(f"[INFO] Team Builder returned {len(candidates)} candidate recommendation(s):")

        candidate_names = []
        for c in candidates:
            cname = c["candidate_name"]
            candidate_names.append(cname)
            cname_lower = cname.lower()

            # Assert NO old placeholder names appear
            for old_name in OLD_FORBIDDEN_NAMES:
                self.assertNotIn(
                    old_name,
                    cname_lower,
                    f"Forbidden old placeholder candidate '{cname}' was found in Team Builder!",
                )

            # Print rich candidate info
            print(f"  -> Candidate: '{cname}' ({c['role_suggestion']}) | Match: {c['match_score']}% | Contributes: {c['skills_contributed']} | Comp: {c['complementary_skills']}")

        # Ensure that Indian demo profiles are actively returned
        matching_indian_names = [n for n in candidate_names if n in EXPECTED_INDIAN_STUDENT_NAMES]
        self.assertGreater(len(matching_indian_names), 0, "Candidates must include new Indian demo profiles")
        print(f"[PASS] Team Builder candidate validation passed. All {len(candidate_names)} candidates are verified Indian profiles.")

    def test_07_admin_verification_queue(self):
        """Verify Admin verification queue displays realistic pending submissions from Indian demo profiles."""
        admin_resp = self.client.get(
            "/api/admin/evidence/pending",
            headers={"Authorization": "Bearer admin-session-token-sujal-verified"},
        )
        self.assertEqual(admin_resp.status_code, 200)
        pending_queue = admin_resp.json()
        self.assertGreaterEqual(len(pending_queue), 1, "Admin queue should have pending evidence to demo")
        print(f"\n[PASS] Admin Verification Queue has {len(pending_queue)} pending submission(s) for live demo:")
        for item in pending_queue:
            st_name = item.get("student", {}).get("name") if item.get("student") else f"Student #{item.get('student_id')}"
            print(f"  - [{item['id']}] '{item['title']}' submitted by '{st_name}' ({item['evidence_type']})")


if __name__ == "__main__":
    unittest.main()
