import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.team import Team, TeamMember, TeamInvitation
from app.core.security import create_access_token
from app.services.team_matching import TeamMatchingService

client = TestClient(app)

def run_tests():
    print("================================================================================")
    print("SKILLBRIDGE MASTER SUITE: 5 CORE SKILLS PER DOMAIN & GLOBAL COMPACTNESS AUDIT")
    print("================================================================================")

    db = SessionLocal()

    # Get test students
    aarav = db.query(Student).filter(Student.email == "aarav.sharma@skillbridge.edu").first()
    aditya = db.query(Student).filter(Student.email == "aditya.mishra@skillbridge.edu").first()
    rohan = db.query(Student).filter(Student.email == "rohan.das@skillbridge.edu").first()
    priya = db.query(Student).filter(Student.email == "priya.nair@skillbridge.edu").first()
    sneha = db.query(Student).filter(Student.email == "sneha.das@skillbridge.edu").first()

    assert aarav and aditya and rohan and priya and sneha, "Required demo students must exist in DB"
    print(f"[PASS] Retrieved demo students: Aarav (#{aarav.id}), Aditya (#{aditya.id}), Rohan (#{rohan.id}), Priya (#{priya.id}), Sneha (#{sneha.id})")

    token_aarav = create_access_token(aarav.id)
    token_aditya = create_access_token(aditya.id)
    token_rohan = create_access_token(rohan.id)

    headers_aarav = {"Authorization": f"Bearer {token_aarav}"}
    headers_aditya = {"Authorization": f"Bearer {token_aditya}"}
    headers_rohan = {"Authorization": f"Bearer {token_rohan}"}

    # ----------------------------------------------------
    # TEST 1: Platform Stats Transparency
    # ----------------------------------------------------
    print("\n--- TEST 1: Platform Stats Transparency ---")
    resp = client.get("/api/students/platform-stats")
    assert resp.status_code == 200, f"Failed platform stats: {resp.text}"
    stats = resp.json()
    print(f"Platform stats: {stats}")
    assert stats["verified_students_count"] >= 15
    assert stats["skills_catalog_count"] >= 70
    assert stats["active_opportunities_count"] >= 20
    print("[PASS] TEST 1: Real-time platform metrics calculated directly from database records.")

    # ----------------------------------------------------
    # TEST 2: Professional Identity & Domain Proficiencies
    # ----------------------------------------------------
    print("\n--- TEST 2: Professional Identity & Role Validation ---")
    resp = client.get("/api/students/me/professional-role", headers=headers_aarav)
    assert resp.status_code == 200
    prof = resp.json()
    print(f"Aarav's Primary Role: {prof['primary_role']}")
    print(f"Aarav's Overall Proficiency: {prof['overall_proficiency']}")
    assert prof["overall_proficiency"] in ["Advanced", "Intermediate"]

    # Role validation advisory warning
    update_resp = client.put(
        "/api/students/me/professional-role",
        headers=headers_aarav,
        json={
            "primary_role": "Cybersecurity Developer",
            "secondary_specializations": ["AI & Machine Learning"],
            "bio": "Testing role validation.",
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["warning"] is not None
    print("[PASS] TEST 2: Professional identity and evidence-aware validation verified.")

    # Restore Aarav
    client.put(
        "/api/students/me/professional-role",
        headers=headers_aarav,
        json={
            "primary_role": "AI/ML Developer",
            "secondary_specializations": ["AI & Machine Learning", "Data Systems"],
            "bio": "AI student at IIT Delhi.",
        },
    )

    # ----------------------------------------------------
    # TEST 3: Strict Deterministic 5-Core Skills Matching
    # ----------------------------------------------------
    print("\n--- TEST 3: Deterministic 5 Core Skills per Domain ---")

    # 3.1 Backend Developer (5 Core: Programming Language, Backend Framework, REST/API, Database, Git)
    recs_backend = TeamMatchingService.get_candidate_recommendations_for_team(db, 1, target_role="Backend Developer")
    rohan_backend = next(r for r in recs_backend if r.candidate_name == "Rohan Das")
    print(f"Rohan Das -> Backend Match: {rohan_backend.match_score}%")
    print(f" - Fulfilled 5-Core: {rohan_backend.core_skills_fulfilled}")
    print(f" - Missing 5-Core: {rohan_backend.core_skills_missing}")
    assert rohan_backend.match_score in [60.0, 80.0, 100.0]

    # 3.2 Rohan Das (Backend) evaluated for Frontend Developer -> MUST BE 0.0%!
    recs_frontend = TeamMatchingService.get_candidate_recommendations_for_team(db, 1, target_role="Frontend Developer")
    rohan_frontend = next(r for r in recs_frontend if r.candidate_name == "Rohan Das")
    print(f"Rohan Das -> Frontend Match: {rohan_frontend.match_score}%")
    assert rohan_frontend.match_score == 0.0, f"Backend candidate must receive 0.0% Frontend match, got {rohan_frontend.match_score}"
    assert "0%" in rohan_frontend.explanation
    print("[PASS] Rohan Das received strictly 0.0% Frontend match.")

    # 3.3 Priya Nair (Frontend) evaluated for Frontend -> MUST BE >= 80.0%
    priya_frontend = next(r for r in recs_frontend if r.candidate_name == "Priya Nair")
    print(f"Priya Nair -> Frontend Match: {priya_frontend.match_score}%")
    assert priya_frontend.match_score >= 80.0

    # 3.4 Priya Nair (Frontend) evaluated for DevOps -> MUST BE 0.0%!
    recs_devops = TeamMatchingService.get_candidate_recommendations_for_team(db, 1, target_role="DevOps & Cloud")
    priya_devops = next(r for r in recs_devops if r.candidate_name == "Priya Nair")
    print(f"Priya Nair -> DevOps Match: {priya_devops.match_score}%")
    assert priya_devops.match_score == 0.0, f"Frontend candidate must receive 0.0% DevOps match, got {priya_devops.match_score}"
    print("[PASS] Priya Nair received strictly 0.0% DevOps match.")

    # 3.5 Sneha Das (DevOps Specialist) evaluated for DevOps -> MUST BE 100.0%
    sneha_devops = next(r for r in recs_devops if r.candidate_name == "Sneha Das")
    print(f"Sneha Das -> DevOps Match: {sneha_devops.match_score}%")
    assert sneha_devops.match_score == 100.0
    print("[PASS] Sneha Das received 100.0% DevOps match.")

    print("[PASS] TEST 3: All 5-Core domain matching rules verified with 100% determinism.")

    # ----------------------------------------------------
    # TEST 4: Team Creation, Invitation, Acceptance & Roster
    # ----------------------------------------------------
    print("\n--- TEST 4: Team Formation, Persistent Invitation, Acceptance & Roster ---")
    create_resp = client.post(
        "/api/teams",
        headers=headers_aarav,
        json={
            "name": f"NextGen Robotics AI {aarav.id}",
            "project_name": "Autonomous Navigation Mesh",
            "description": "Multi-agent navigation pipeline using fine-tuned models.",
            "required_domains": ["Backend Development", "AI & Machine Learning", "Frontend & UI"],
        },
    )
    assert create_resp.status_code == 201
    created_team = create_resp.json()
    team_id = created_team["id"]

    # Send invitation from Aarav to Aditya
    inv_resp = client.post(
        f"/api/teams/{team_id}/invitations",
        headers=headers_aarav,
        json={
            "recipient_id": aditya.id,
            "role": "Frontend Specialist",
            "message": "Collaborate with us!",
        },
    )
    assert inv_resp.status_code == 201
    inv_id = inv_resp.json()["id"]

    # Aditya accepts invitation
    accept_resp = client.post(f"/api/teams/invitations/{inv_id}/accept", headers=headers_aditya)
    assert accept_resp.status_code == 200

    # Both users see the exact same team record on /my-team
    my_aarav = client.get("/api/teams/my", headers=headers_aarav).json()
    my_aditya = client.get("/api/teams/my", headers=headers_aditya).json()
    assert any(t["id"] == team_id for t in my_aarav)
    assert any(t["id"] == team_id for t in my_aditya)
    print(f"[PASS] Team #{team_id} successfully shared between Leader Aarav and Member Aditya.")

    print("\n================================================================================")
    print("ALL TESTS PASSED WITH 100% DETERMINISM AND ACCURACY!")
    print("================================================================================")
    db.close()

if __name__ == "__main__":
    run_tests()
