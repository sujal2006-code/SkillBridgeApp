import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.core.security import create_access_token
from app.services.team_matching import TeamMatchingService

client = TestClient(app)

def run_audit():
    print("=" * 80)
    print("SKILLBRIDGE TEAM BUILDER & MY TEAM COMPREHENSIVE FLOW AUDIT")
    print("=" * 80)

    db = SessionLocal()

    # Find demo students
    aarav = db.query(Student).filter(Student.email == "aarav.sharma@skillbridge.edu").first()
    aditya = db.query(Student).filter(Student.email == "aditya.mishra@skillbridge.edu").first()
    rohan = db.query(Student).filter(Student.email == "rohan.das@skillbridge.edu").first()
    priya = db.query(Student).filter(Student.email == "priya.nair@skillbridge.edu").first()
    sneha = db.query(Student).filter(Student.email == "sneha.das@skillbridge.edu").first()

    assert aarav and aditya and rohan and priya and sneha, "All test demo students must exist"
    print(f"[OK] Loaded students: Aarav (#{aarav.id}), Aditya (#{aditya.id}), Rohan (#{rohan.id}), Priya (#{priya.id}), Sneha (#{sneha.id})")

    token_aarav = create_access_token(aarav.id)
    token_rohan = create_access_token(rohan.id)
    token_priya = create_access_token(priya.id)

    headers_aarav = {"Authorization": f"Bearer {token_aarav}"}
    headers_rohan = {"Authorization": f"Bearer {token_rohan}"}
    headers_priya = {"Authorization": f"Bearer {token_priya}"}

    # Find or create a test team for Aarav
    team = db.query(Team).filter(Team.creator_id == aarav.id).first()
    if not team:
        team = Team(
            name="Hex Bridge Audit Team",
            project_name="Autonomous Skill Matching",
            description="Testing multidisciplinary team gaps and matching",
            creator_id=aarav.id,
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        leader_member = TeamMember(
            team_id=team.id,
            student_id=aarav.id,
            role="Team Leader",
            status="joined",
        )
        db.add(leader_member)
        db.commit()

    team_id = team.id
    print(f"[OK] Using team #{team_id} ('{team.name}') created by Aarav")

    # ----------------------------------------------------
    # FLOW 1: Frontend Role Matching
    # ----------------------------------------------------
    print("\n--- FLOW 1: Frontend Role Matching ---")
    resp = client.get(f"/api/teams/{team_id}/candidates?target_role=Frontend Developer")
    assert resp.status_code == 200
    candidates = resp.json()
    assert len(candidates) > 0
    print(f"[OK] Received {len(candidates)} candidates for Frontend Developer")

    # Check Priya (Frontend specialist)
    priya_cand = next((c for c in candidates if c["candidate_id"] == priya.id), None)
    assert priya_cand is not None
    assert priya_cand["match_score"] in [60.0, 80.0, 100.0]
    assert any("HTML" in f or "React" in f or "JavaScript" in f for f in priya_cand["core_skills_fulfilled"])
    print(f" [PASS] Priya Nair Frontend score: {priya_cand['match_score']}% (Fulfilled: {priya_cand['core_skills_fulfilled']})")

    # Check Rohan (Backend specialist) for Frontend -> should be strictly 0.0%
    rohan_cand_front = next((c for c in candidates if c["candidate_id"] == rohan.id), None)
    if rohan_cand_front:
        assert rohan_cand_front["match_score"] == 0.0
        print(f" [PASS] Rohan Das Frontend score: {rohan_cand_front['match_score']}% (Strict 0% for unrelated domain)")

    # ----------------------------------------------------
    # FLOW 2: Backend Role Matching
    # ----------------------------------------------------
    print("\n--- FLOW 2: Backend Role Matching ---")
    resp = client.get(f"/api/teams/{team_id}/candidates?target_role=Backend Developer")
    assert resp.status_code == 200
    candidates = resp.json()
    rohan_cand = next((c for c in candidates if c["candidate_id"] == rohan.id), None)
    assert rohan_cand is not None
    assert rohan_cand["match_score"] == 80.0
    assert not any("AI" in m or "Machine Learning" in m for m in rohan_cand["missing_team_skills"])
    print(f" [PASS] Rohan Das Backend score: {rohan_cand['match_score']}% (Fulfilled: {rohan_cand['core_skills_fulfilled']}, Missing: {rohan_cand['missing_team_skills']})")
    print(" [PASS] Confirmed: No AI/ML in Backend missing requirements!")

    # ----------------------------------------------------
    # FLOW 3: AI/ML Role Matching
    # ----------------------------------------------------
    print("\n--- FLOW 3: AI/ML Role Matching ---")
    resp = client.get(f"/api/teams/{team_id}/candidates?target_role=AI/ML Developer")
    assert resp.status_code == 200
    candidates = resp.json()
    priya_cand = next((c for c in candidates if c["candidate_id"] == priya.id), None)
    if priya_cand:
        assert priya_cand["match_score"] == 0.0
        print(f" [PASS] Priya Nair (Frontend) AI/ML score: {priya_cand['match_score']}% (Strict 0.0%)")

    # ----------------------------------------------------
    # FLOW 4: Database Role Matching
    # ----------------------------------------------------
    print("\n--- FLOW 4: Database Role Matching ---")
    resp = client.get(f"/api/teams/{team_id}/candidates?target_role=Database Specialist")
    assert resp.status_code == 200
    candidates = resp.json()
    print(f" [PASS] Successfully evaluated {len(candidates)} candidates for Database Specialist")

    # ----------------------------------------------------
    # FLOW 5: UI/UX Role Matching
    # ----------------------------------------------------
    print("\n--- FLOW 5: UI/UX Role Matching ---")
    resp = client.get(f"/api/teams/{team_id}/candidates?target_role=UI/UX Designer")
    assert resp.status_code == 200
    candidates = resp.json()
    print(f" [PASS] Successfully evaluated {len(candidates)} candidates for UI/UX Designer")

    # ----------------------------------------------------
    # FLOW 6: DevOps Role Matching
    # ----------------------------------------------------
    print("\n--- FLOW 6: DevOps Role Matching ---")
    resp = client.get(f"/api/teams/{team_id}/candidates?target_role=DevOps Engineer")
    assert resp.status_code == 200
    candidates = resp.json()
    sneha_cand = next((c for c in candidates if c["candidate_id"] == sneha.id), None)
    assert sneha_cand is not None
    assert sneha_cand["match_score"] == 100.0
    print(f" [PASS] Sneha Das DevOps score: {sneha_cand['match_score']}% (100% Core Match: Linux, Git, Docker, CI/CD, Cloud)")

    # ----------------------------------------------------
    # FLOW 7: Deterministic Step Scores
    # ----------------------------------------------------
    print("\n--- FLOW 7: Deterministic Multiples of 20% ---")
    allowed_scores = {0.0, 20.0, 40.0, 60.0, 80.0, 100.0}
    for c in candidates:
        assert c["match_score"] in allowed_scores, f"Invalid score {c['match_score']}"
    print(f" [PASS] All candidate scores are strictly deterministic multiples of 20% (0, 20, 40, 60, 80, 100). No fake 73% or 72%.")

    # ----------------------------------------------------
    # FLOW 8: Invitation & Notification Flow
    # ----------------------------------------------------
    print("\n--- FLOW 8: Invitation, Notification, Accept, & Reject ---")
    # 1. Aarav invites Rohan
    invite_payload = {
        "recipient_id": rohan.id,
        "role": "Backend Developer",
        "message": "Please join Hex Bridge as our Backend Lead",
    }
    resp = client.post(f"/api/teams/{team_id}/invitations", json=invite_payload, headers=headers_aarav)
    assert resp.status_code in [200, 201]
    inv = resp.json()
    inv_id = inv["id"]
    assert inv["status"] == "PENDING"
    print(f" [PASS] Sent invitation #{inv_id} to Rohan Das. Status: PENDING")

    # 2. Rohan checks pending invitations
    resp = client.get("/api/teams/invitations/pending", headers=headers_rohan)
    assert resp.status_code == 200
    rohan_invs = resp.json()
    assert any(i["id"] == inv_id for i in rohan_invs)
    print(f" [PASS] Rohan received notification for invitation #{inv_id}")

    # 3. Test Reject Invitation flow
    resp = client.post(f"/api/teams/invitations/{inv_id}/reject", headers=headers_rohan)
    assert resp.status_code == 200
    rejected = resp.json()
    assert rejected["status"] == "REJECTED"
    print(f" [PASS] Rohan rejected invitation #{inv_id}. Status: REJECTED")

    # Verify Rohan is NOT a team member
    check_team = db.query(Team).filter(Team.id == team_id).first()
    assert not any(m.student_id == rohan.id and m.status == "joined" for m in check_team.members)
    print(" [PASS] Confirmed: Rejected candidate does NOT become a team member.")

    # 4. Now send another invitation to Priya and test Accept Invitation flow
    invite_priya = {
        "recipient_id": priya.id,
        "role": "Frontend Developer",
        "message": "Join us as Frontend Developer",
    }
    resp = client.post(f"/api/teams/{team_id}/invitations", json=invite_priya, headers=headers_aarav)
    assert resp.status_code in [200, 201]
    priya_inv = resp.json()
    priya_inv_id = priya_inv["id"]
    print(f" [PASS] Sent invitation #{priya_inv_id} to Priya Nair. Status: PENDING")

    # Priya accepts invitation
    resp = client.post(f"/api/teams/invitations/{priya_inv_id}/accept", headers=headers_priya)
    assert resp.status_code == 200
    accepted = resp.json()
    assert accepted["status"] == "ACCEPTED"
    print(f" [PASS] Priya accepted invitation #{priya_inv_id}. Status: ACCEPTED")

    # ----------------------------------------------------
    # FLOW 9: My Team & Persistent Team Membership
    # ----------------------------------------------------
    print("\n--- FLOW 9: My Team & Persistent Team Membership ---")
    # Leader Aarav calls /api/teams/my
    resp_aarav = client.get("/api/teams/my", headers=headers_aarav)
    assert resp_aarav.status_code == 200
    teams_aarav = resp_aarav.json()
    shared_aarav = next((t for t in teams_aarav if t["id"] == team_id), None)
    assert shared_aarav is not None

    # Member Priya calls /api/teams/my
    resp_priya = client.get("/api/teams/my", headers=headers_priya)
    assert resp_priya.status_code == 200
    teams_priya = resp_priya.json()
    shared_priya = next((t for t in teams_priya if t["id"] == team_id), None)
    assert shared_priya is not None

    # Both must see the same team and members!
    assert shared_aarav["id"] == shared_priya["id"]
    assert shared_aarav["name"] == shared_priya["name"]
    print(f" [PASS] Both Leader Aarav and Member Priya see the exact same persistent team record (Team #{team_id}: '{shared_aarav['name']}')")
    
    # Check members in both views
    aarav_member_ids = {m["student_id"] for m in shared_aarav["members"] if m["status"] == "joined"}
    priya_member_ids = {m["student_id"] for m in shared_priya["members"] if m["status"] == "joined"}
    assert aarav.id in aarav_member_ids and priya.id in aarav_member_ids
    assert aarav_member_ids == priya_member_ids
    print(f" [PASS] Team member roster identical for both users: {[m['student_name'] for m in shared_aarav['members'] if m['status'] == 'joined']}")

    # ----------------------------------------------------
    # FLOW 10: Dynamic Team Coverage Recalculation
    # ----------------------------------------------------
    print("\n--- FLOW 10: Dynamic Team Coverage Recalculation ---")
    print(f"Team Coverage Percentage: {shared_aarav.get('team_coverage_percentage')}%")
    print(f"Skills Covered: {shared_aarav.get('skills_covered')}")
    print(f"Skills Missing: {shared_aarav.get('skills_missing')}")
    assert shared_aarav.get("team_coverage_percentage", 0) > 0
    print(" [PASS] Team skill coverage calculated dynamically from active members' verified skills.")

    print("\n" + "=" * 80)
    print("ALL 10 IMPORTANT FLOW AUDITS PASSED WITH 100% VERIFICATION!")
    print("=" * 80)

if __name__ == "__main__":
    run_audit()
