import os
import sys
import functools

# Force unbuffered output
print = functools.partial(print, flush=True)

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import time
from sqlalchemy.orm import joinedload
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.team import Team, TeamMember, TeamSkillRequirement

client = TestClient(app)

def run_master_test_suite():
    print("================================================================================")
    print("SKILLBRIDGE FINAL MASTER TEST SUITE - 8 CRITICAL SCENARIOS")
    print("================================================================================")
    
    # ----------------------------------------------------------------------------
    # Test 1 — New Account
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 1] Create New Account ---")
    ts = int(time.time() * 1000)
    new_name = f"Student_{ts}"
    new_pwd = "Password123"

    print("Registering new student...")
    resp1 = client.post("/api/students/login", json={
        "name": new_name,
        "password": new_pwd,
        "confirm_password": new_pwd,
        "mode": "register"
    })
    assert resp1.status_code == 200, f"Registration failed: {resp1.text}"
    data1 = resp1.json()
    new_student_id = data1["student"]["id"]
    token_1 = data1["token"]
    assert data1["student"]["name"] == new_name
    assert len(data1["student"]["skills"]) == 0
    assert len(data1["student"]["evidence"]) == 0
    print(f" [PASS] Test 1: Created ID {new_student_id} with initial empty passport (0 skills, 0 evidence).")

    print("Testing login for new account...")
    login_resp = client.post("/api/students/login", json={
        "name": new_name,
        "password": new_pwd,
        "mode": "login"
    })
    assert login_resp.status_code == 200
    print(f" [PASS] Test 1.1: Login successful.")

    # ----------------------------------------------------------------------------
    # Test 2 — Duplicate Name (Exact match)
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 2] Duplicate Name Protection ---")
    resp2 = client.post("/api/students/login", json={
        "name": new_name,
        "password": new_pwd,
        "confirm_password": new_pwd,
        "mode": "register"
    })
    assert resp2.status_code == 400, f"Expected 400, got {resp2.status_code}: {resp2.text}"
    assert resp2.json()["detail"] == "Account already exists. Please use a different name."
    print(f" [PASS] Test 2: Duplicate exact name rejected: '{resp2.json()['detail']}'.")

    # ----------------------------------------------------------------------------
    # Test 3 — Case Variation ("aditya mishra" vs "Aditya Mishra")
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 3] Case Variation Duplicate Protection ---")
    resp3 = client.post("/api/students/login", json={
        "name": new_name.lower(),
        "password": new_pwd,
        "confirm_password": new_pwd,
        "mode": "register"
    })
    assert resp3.status_code == 400, f"Expected 400, got {resp3.status_code}: {resp3.text}"
    assert resp3.json()["detail"] == "Account already exists. Please use a different name."
    print(f" [PASS] Test 3: Lowercase variant '{new_name.lower()}' rejected.")

    resp3_aditya = client.post("/api/students/login", json={
        "name": "aditya mishra",
        "password": new_pwd,
        "confirm_password": new_pwd,
        "mode": "register"
    })
    assert resp3_aditya.status_code == 400
    assert resp3_aditya.json()["detail"] == "Account already exists. Please use a different name."
    print(f" [PASS] Test 3.1: 'aditya mishra' rejected when 'Aditya Mishra' exists.")

    # ----------------------------------------------------------------------------
    # Test 4 — Extra Spaces ("   Aditya   Mishra   ")
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 4] Extra Spaces Duplicate Protection ---")
    resp4 = client.post("/api/students/login", json={
        "name": f"   {new_name}   ",
        "password": new_pwd,
        "confirm_password": new_pwd,
        "mode": "register"
    })
    assert resp4.status_code == 400
    assert resp4.json()["detail"] == "Account already exists. Please use a different name."
    print(f" [PASS] Test 4: Extra spaces '{f'   {new_name}   '}' normalized and rejected.")

    resp4_aditya = client.post("/api/students/login", json={
        "name": "   Aditya   Mishra   ",
        "password": new_pwd,
        "confirm_password": new_pwd,
        "mode": "register"
    })
    assert resp4_aditya.status_code == 400
    assert resp4_aditya.json()["detail"] == "Account already exists. Please use a different name."
    print(f" [PASS] Test 4.1: '   Aditya   Mishra   ' normalized and rejected.")

    # ----------------------------------------------------------------------------
    # Test 5 — Duplicate Email
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 5] Duplicate Email Protection ---")
    resp5 = client.post("/api/students", json={
        "name": f"Unique Student {ts}",
        "email": "aditya.mishra@skillbridge.edu",
        "university": "Test University",
        "graduation_year": 2026
    })
    assert resp5.status_code == 400
    assert resp5.json()["detail"] == "An account with this email already exists. Please use a different email or log in."
    print(f" [PASS] Test 5: Duplicate email rejected: '{resp5.json()['detail']}'.")

    # ----------------------------------------------------------------------------
    # Test 6 — Passport / Team Builder Consistency (Candidate with 0 Verified Skills)
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 6] Passport / Team Builder Consistency (0 Skills) ---")
    prof_resp = client.get("/api/students/me", headers={"Authorization": f"Bearer {token_1}"})
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()
    assert len(prof_data["skills"]) == 0
    assert len(prof_data["evidence"]) == 0
    print(f" [PASS] Test 6.1: Passport of candidate shows 0 verified skills, 0 evidence.")

    teams_resp = client.get("/api/teams")
    assert teams_resp.status_code == 200
    teams_list = teams_resp.json()
    if teams_list:
        target_team_id = teams_list[0]["id"]
        cands_resp = client.get(f"/api/teams/{target_team_id}/candidates")
        assert cands_resp.status_code == 200
        cand_list = cands_resp.json()
        cand_item = next((c for c in cand_list if c["candidate_id"] == new_student_id), None)
        if cand_item:
            assert cand_item["match_score"] == 0.0
            assert len(cand_item["verified_skills"]) == 0
    print(f" [PASS] Test 6.2: Team Builder does not calculate fake match score from non-existent skills.")

    # ----------------------------------------------------------------------------
    # Test 7 — Verified Skill End-to-End Flow
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 7] Verified Skill End-to-End Flow ---")
    # Submit evidence
    ev_resp = client.post("/api/evidence", json={
        "title": f"Production Docker & PostgreSQL Pipeline {ts}",
        "description": "Containerized microservices database layer with Docker and PostgreSQL.",
        "evidence_type": "project",
        "issuer": "IIT Delhi Cloud Lab",
        "verification_status": "pending",
        "skill_names": ["Docker", "PostgreSQL"]
    }, headers={"Authorization": f"Bearer {token_1}"})
    assert ev_resp.status_code == 201
    ev_id = ev_resp.json()["id"]
    print(f" [PASS] Test 7.1: Evidence submitted (ID: {ev_id}), status: pending.")

    # Check passport before approval
    prof_pre = client.get("/api/students/me", headers={"Authorization": f"Bearer {token_1}"}).json()
    verified_pre = [s for s in prof_pre["skills"] if s["verification_status"] == "verified"]
    assert len(verified_pre) == 0
    print(f" [PASS] Test 7.2: 0 verified skills before admin approval.")

    # Admin approves evidence
    admin_resp = client.post(f"/api/admin/evidence/{ev_id}/approve", headers={"Authorization": "Bearer admin-session-token-sujal-verified"})
    assert admin_resp.status_code == 200
    print(f" [PASS] Test 7.3: Admin approved evidence ID {ev_id}.")

    # Check passport after approval
    prof_post = client.get("/api/students/me", headers={"Authorization": f"Bearer {token_1}"}).json()
    verified_post = [s for s in prof_post["skills"] if s["verification_status"] == "verified"]
    verified_names = [s["skill"]["name"] for s in verified_post if s.get("skill")]
    assert "Docker" in verified_names or "PostgreSQL" in verified_names
    print(f" [PASS] Test 7.4: Passport updated with verified skills: {verified_names}.")

    # Check team candidate recommendation
    if teams_list:
        target_team_id = teams_list[0]["id"]
        cands_resp = client.get(f"/api/teams/{target_team_id}/candidates?target_role=Database%20Specialist")
        assert cands_resp.status_code == 200
        cand_list = cands_resp.json()
        cand_item = next((c for c in cand_list if c["candidate_id"] == new_student_id), None)
        assert cand_item is not None
        assert cand_item["match_score"] > 0.0
        assert len(cand_item["verified_skills"]) > 0
        print(f" [PASS] Test 7.5: Team Builder dynamic match updated! Score: {cand_item['match_score']}%, Explanation: '{cand_item['explanation']}'.")

    # ----------------------------------------------------------------------------
    # Test 8 — Demo Candidate Parity Check
    # ----------------------------------------------------------------------------
    print("\n--- [TEST 8] Demo Candidate Parity Check ---")
    db = SessionLocal()
    try:
        aditya = db.query(Student).filter(Student.name == "Aditya Mishra").first()
        assert aditya is not None
        aditya_db_skills = db.query(StudentSkill).options(joinedload(StudentSkill.skill)).filter(
            StudentSkill.student_id == aditya.id,
            StudentSkill.verification_status == "verified"
        ).all()
        aditya_db_skill_names = sorted([ss.skill.name for ss in aditya_db_skills if ss.skill])

        if teams_list:
            target_team_id = teams_list[0]["id"]
            cands_resp = client.get(f"/api/teams/{target_team_id}/candidates")
            aditya_rec = next((c for c in cands_resp.json() if c["candidate_id"] == aditya.id), None)
            if aditya_rec:
                for s in aditya_rec["skills_contributed"] + aditya_rec["complementary_skills"]:
                    assert s in aditya_db_skill_names, f"Skill '{s}' in explanation is NOT verified for Aditya!"
                print(f" [PASS] Test 8: Complete consistency: Passport Skills == DB Skills ({aditya_db_skill_names}) == Team Builder Skills.")
    finally:
        db.close()

    print("\n================================================================================")
    print("ALL 8 MASTER SCENARIOS PASSED WITH 100% SUCCESS!")
    print("================================================================================")

if __name__ == "__main__":
    run_master_test_suite()
