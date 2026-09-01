import os
import sys

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.team import Team, TeamMember, TeamInvitation
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.professional_role import StudentProfessionalProfile
from app.core.security import create_access_token

def run_test_suite():
    print("=" * 80)
    print("SKILLBRIDGE RIGOROUS VERIFICATION: CLEAN DEMO STATE + REAL INVITATION FLOW")
    print("=" * 80)

    client = TestClient(app)
    db = SessionLocal()

    # --------------------------------------------------------------------------
    # 1. VERIFY CLEAN INITIAL DATABASE STATE (NO OLD PERSONAL/TEST USERS OR TEAMS)
    # --------------------------------------------------------------------------
    print("\n--- 1. Clean Initial Database State Audit ---")
    forbidden_names = ["sujal sahu", "somadutta sahu", "shiva mishra", "alex rivera"]
    for fn in forbidden_names:
        found = db.query(Student).filter(Student.name.ilike(f"%{fn}%")).first()
        assert found is None, f"FORBIDDEN student '{fn}' still found in database!"
    print(" [PASS] Confirmed: Sujal Sahu, Somadutta Sahu, Shiva Mishra, and Alex Rivera are NOT in the database.")

    total_teams_initial = db.query(Team).count()
    assert total_teams_initial == 0, f"Expected 0 initial teams in clean state, got {total_teams_initial}"
    print(" [PASS] Confirmed: Total initial teams = 0 (clean slate).")

    # --------------------------------------------------------------------------
    # 2. VERIFY PROPER DEMO ACCOUNTS
    # --------------------------------------------------------------------------
    print("\n--- 2. Canonical Demo Student Accounts Audit ---")
    arjun = db.query(Student).filter(Student.name.ilike("%arjun patel%")).first()
    rohan = db.query(Student).filter(Student.name.ilike("%rohan das%")).first()
    priya = db.query(Student).filter(Student.name.ilike("%priya nair%")).first()
    ananya = db.query(Student).filter(Student.name.ilike("%ananya singh%")).first()
    abhishek = db.query(Student).filter(Student.name.ilike("%abhishek mohanty%")).first()
    neha = db.query(Student).filter(Student.name.ilike("%neha sharma%")).first()

    assert arjun is not None, "Arjun Patel must exist"
    assert rohan is not None, "Rohan Das must exist"
    assert priya is not None, "Priya Nair must exist"
    assert ananya is not None, "Ananya Singh must exist"
    assert abhishek is not None, "Abhishek Mohanty must exist"
    assert neha is not None, "Neha Sharma must exist"

    print(f" [PASS] Arjun Patel: #{arjun.id} ({arjun.university}) - Role: {arjun.professional_profile.primary_role}")
    print(f" [PASS] Rohan Das: #{rohan.id} ({rohan.university}) - Role: {rohan.professional_profile.primary_role}")
    print(f" [PASS] Priya Nair: #{priya.id} ({priya.university}) - Role: {priya.professional_profile.primary_role}")
    print(f" [PASS] Ananya Singh: #{ananya.id} ({ananya.university}) - Role: {ananya.professional_profile.primary_role}")
    print(f" [PASS] Abhishek Mohanty: #{abhishek.id} ({abhishek.university}) - Role: {abhishek.professional_profile.primary_role}")
    print(f" [PASS] Neha Sharma: #{neha.id} ({neha.university}) - Role: {neha.professional_profile.primary_role}")

    # --------------------------------------------------------------------------
    # 3. MY TEAM STARTS CLEAN (EMPTY STATE FOR USERS WITH NO TEAM)
    # --------------------------------------------------------------------------
    print("\n--- 3. My Team Starts Clean for Users Without Teams ---")
    token_arjun = create_access_token(arjun.id)
    token_priya = create_access_token(priya.id)
    headers_arjun = {"Authorization": f"Bearer {token_arjun}"}
    headers_priya = {"Authorization": f"Bearer {token_priya}"}

    arjun_teams = client.get("/api/teams/my", headers=headers_arjun).json()
    priya_teams = client.get("/api/teams/my", headers=headers_priya).json()

    assert len(arjun_teams) == 0, f"Expected Arjun to have 0 teams, got {len(arjun_teams)}"
    assert len(priya_teams) == 0, f"Expected Priya to have 0 teams, got {len(priya_teams)}"
    print(" [PASS] Confirmed: /api/teams/my returns [] (Clean empty state: 'You are not part of a project team yet').")

    # --------------------------------------------------------------------------
    # 4. USER A CREATES A TEAM
    # --------------------------------------------------------------------------
    print("\n--- 4. User A (Arjun Patel) Creates Team 'NeuroVision AI' ---")
    create_payload = {
        "name": "NeuroVision AI",
        "project_name": "Autonomous Computer Vision & Edge Intelligence",
        "description": "Multidisciplinary team for computer vision and edge diagnostics.",
        "creator_id": arjun.id,
        "required_domains": ["AI/ML", "Frontend", "Backend"],
    }
    create_resp = client.post("/api/teams", json=create_payload, headers=headers_arjun)
    assert create_resp.status_code == 201, f"Team creation failed: {create_resp.text}"
    team_data = create_resp.json()
    team_id = team_data["id"]
    print(f" [PASS] Team #{team_id} '{team_data['name']}' created by Arjun Patel.")

    # Check Arjun's My Team
    arjun_teams_after = client.get("/api/teams/my", headers=headers_arjun).json()
    assert len(arjun_teams_after) == 1
    my_team = arjun_teams_after[0]
    assert my_team["id"] == team_id
    assert my_team["creator_id"] == arjun.id
    assert len(my_team["members"]) == 1
    assert my_team["members"][0]["role"] == "Team Leader"
    assert my_team["members"][0]["status"] == "joined"
    print(f" [PASS] Arjun sees Team #{team_id}: Arjun = Team Leader, Members = 1/6.")

    # Check Priya's My Team (She has NOT been invited or joined yet, so still 0)
    priya_teams_check = client.get("/api/teams/my", headers=headers_priya).json()
    assert len(priya_teams_check) == 0, "Priya must still see 0 teams."
    print(" [PASS] Priya still sees clean 0 teams.")

    # --------------------------------------------------------------------------
    # 5. USER A INVITES USER B (PENDING STATE)
    # --------------------------------------------------------------------------
    print("\n--- 5. User A Invites User B (Priya Nair) -> PENDING State ---")
    invite_payload = {
        "recipient_id": priya.id,
        "role": "Frontend Developer",
        "message": "Join NeuroVision AI as Frontend Developer",
    }
    invite_resp = client.post(f"/api/teams/{team_id}/invitations", json=invite_payload, headers=headers_arjun)
    assert invite_resp.status_code in [200, 201], f"Invitation failed: {invite_resp.text}"
    inv_data = invite_resp.json()
    inv_id = inv_data["id"]
    assert inv_data["status"] == "PENDING"
    print(f" [PASS] Invitation #{inv_id} created with status 'PENDING'.")

    # Member count check: PENDING must NOT count toward accepted membership!
    team_check = client.get("/api/teams/my", headers=headers_arjun).json()[0]
    assert len(team_check["members"]) == 1, "Pending invitee must NOT be in accepted members list!"
    assert not any(m["student_id"] == priya.id for m in team_check["members"]), "Priya must not be a member yet!"
    print(" [PASS] Confirmed: Team member count remains exactly 1/6. Pending invitee does NOT count as member.")

    # Priya receives pending notification
    pending_notifs = client.get("/api/teams/invitations/pending", headers=headers_priya).json()
    assert any(p["id"] == inv_id for p in pending_notifs), "Priya must see the pending invitation in notifications!"
    print(f" [PASS] Priya sees Invitation #{inv_id} in her pending invitations area.")

    # --------------------------------------------------------------------------
    # 6. USER B ACCEPTS INVITATION -> SHARED PERSISTENT TEAM
    # --------------------------------------------------------------------------
    print("\n--- 6. User B Accepts Invitation -> Single Shared Team ---")
    accept_resp = client.post(f"/api/teams/invitations/{inv_id}/accept", headers=headers_priya)
    assert accept_resp.status_code == 200, f"Accept failed: {accept_resp.text}"
    assert accept_resp.json()["status"] == "ACCEPTED"
    print(f" [PASS] Invitation #{inv_id} status updated to 'ACCEPTED'.")

    # Check Arjun's view
    arjun_view = client.get("/api/teams/my", headers=headers_arjun).json()[0]
    assert arjun_view["id"] == team_id
    assert len(arjun_view["members"]) == 2
    priya_in_arjun_team = next(m for m in arjun_view["members"] if m["student_id"] == priya.id)
    assert priya_in_arjun_team["status"] == "joined"
    assert priya_in_arjun_team["role"] == "Frontend Developer"
    print(f" [PASS] Arjun sees: Team #{team_id}, Leader: Arjun Patel, Member: Priya Nair, 2/6 Members.")

    # Check Priya's view
    priya_view = client.get("/api/teams/my", headers=headers_priya).json()[0]
    assert priya_view["id"] == team_id, "Both users MUST receive the exact same team ID!"
    assert priya_view["creator_id"] == arjun.id
    assert priya_view["creator_name"] == "Arjun Patel"
    assert len(priya_view["members"]) == 2
    print(f" [PASS] Priya sees the SAME Team #{team_id} (Created by Arjun Patel), 2/6 Members.")

    # --------------------------------------------------------------------------
    # 7. PERSISTENCE ACROSS REFRESH, LOGOUT & RELOGIN
    # --------------------------------------------------------------------------
    print("\n--- 7. Persistence Across Session Wipe & Relogin ---")
    # Simulate completely fresh sessions
    login_arjun = client.post("/api/students/login", json={"name": "Arjun Patel", "password": "skillbridge2026", "mode": "login"})
    login_priya = client.post("/api/students/login", json={"name": "Priya Nair", "password": "skillbridge2026", "mode": "login"})
    assert login_arjun.status_code == 200 and login_priya.status_code == 200

    new_h_arjun = {"Authorization": f"Bearer {login_arjun.json()['token']}"}
    new_h_priya = {"Authorization": f"Bearer {login_priya.json()['token']}"}

    recheck_arjun = client.get("/api/teams/my", headers=new_h_arjun).json()[0]
    recheck_priya = client.get("/api/teams/my", headers=new_h_priya).json()[0]

    assert recheck_arjun["id"] == team_id and recheck_priya["id"] == team_id
    assert len(recheck_arjun["members"]) == 2 and len(recheck_priya["members"]) == 2
    print(" [PASS] Confirmed: Team #{team_id} and memberships persist identically across logout/relogin!")

    # --------------------------------------------------------------------------
    # 8. INVITATION REJECTION LIFECYCLE
    # --------------------------------------------------------------------------
    print("\n--- 8. Rejection Test: Arjun Invites Rohan -> Rohan Rejects ---")
    invite_rohan = {
        "recipient_id": rohan.id,
        "role": "Backend Developer",
        "message": "Join us on NeuroVision AI",
    }
    inv_rohan_resp = client.post(f"/api/teams/{team_id}/invitations", json=invite_rohan, headers=headers_arjun)
    assert inv_rohan_resp.status_code in [200, 201]
    inv_rohan_id = inv_rohan_resp.json()["id"]

    token_rohan = create_access_token(rohan.id)
    headers_rohan = {"Authorization": f"Bearer {token_rohan}"}

    # Rohan rejects
    reject_resp = client.post(f"/api/teams/invitations/{inv_rohan_id}/reject", headers=headers_rohan)
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"
    print(f" [PASS] Rohan rejected Invitation #{inv_rohan_id}.")

    # Confirm Rohan is NOT a member
    after_reject_team = client.get("/api/teams/my", headers=headers_arjun).json()[0]
    assert len(after_reject_team["members"]) == 2, "Team member count must remain 2!"
    assert not any(m["student_id"] == rohan.id for m in after_reject_team["members"])
    print(" [PASS] Confirmed: Rejected candidate does NOT appear in team roster.")

    # --------------------------------------------------------------------------
    # 9. REAL REGISTERED USER -> DISCOVERABLE IN TEAM BUILDER
    # --------------------------------------------------------------------------
    print("\n--- 9. Real Registered Student -> Team Builder Discovery ---")
    reg_payload = {
        "name": "Kunal Roy",
        "password": "skillbridge2026",
        "confirm_password": "skillbridge2026",
        "mode": "register",
    }
    reg_resp = client.post("/api/students/login", json=reg_payload)
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    new_student = reg_resp.json()["student"]
    new_token = reg_resp.json()["token"]
    headers_kunal = {"Authorization": f"Bearer {new_token}"}
    print(f" [PASS] New real student registered: Kunal Roy (#{new_student['id']}).")

    # Kunal sets his role to Backend Developer
    kunal_prof = client.put("/api/students/me/professional-role", json={"primary_role": "Backend Developer"}, headers=headers_kunal)
    assert kunal_prof.status_code == 200, f"Role update failed: {kunal_prof.text}"
    print(" [PASS] Kunal set professional role to 'Backend Developer'.")

    # Add verified skills to Kunal
    sk_python = db.query(Skill).filter(Skill.name.ilike("python")).first()
    sk_fastapi = db.query(Skill).filter(Skill.name.ilike("fastapi")).first()
    sk_sql = db.query(Skill).filter(Skill.name.ilike("%sql%")).first()
    sk_rest = db.query(Skill).filter(Skill.name.ilike("%rest%")).first()
    sk_git = db.query(Skill).filter(Skill.name.ilike("git")).first()

    for sk in [sk_python, sk_fastapi, sk_sql, sk_rest, sk_git]:
        if sk:
            db.add(StudentSkill(
                student_id=new_student["id"],
                skill_id=sk.id,
                proficiency_level="Advanced",
                verification_status="verified",
            ))
    db.commit()
    print(" [PASS] Added verified backend skills to Kunal Roy.")

    # Arjun searches for Backend Developer in Team Builder
    candidates_resp = client.get(f"/api/teams/{team_id}/candidates?target_role=Backend+Developer", headers=headers_arjun)
    assert candidates_resp.status_code == 200
    cand_list = candidates_resp.json()

    kunal_rec = next((c for c in cand_list if c["candidate_id"] == new_student["id"]), None)
    assert kunal_rec is not None, "Newly registered user Kunal Roy MUST appear in Team Builder!"
    assert kunal_rec["target_role"] == "Backend Developer"
    assert kunal_rec["match_score"] >= 80.0, f"Expected high match score, got {kunal_rec['match_score']}"
    assert len(kunal_rec["core_skills_fulfilled"]) >= 4
    print(f" [PASS] Kunal Roy discovered in Team Builder: Match Score: {kunal_rec['match_score']}%, Fulfilled 5-Core: {kunal_rec['core_skills_fulfilled']}")

    # Clean up test records
    db.query(StudentSkill).filter(StudentSkill.student_id == new_student["id"]).delete()
    db.query(StudentProfessionalProfile).filter(StudentProfessionalProfile.student_id == new_student["id"]).delete()
    db.query(Student).filter(Student.id == new_student["id"]).delete()
    db.query(TeamInvitation).filter(TeamInvitation.team_id == team_id).delete()
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    db.query(Team).filter(Team.id == team_id).delete()
    db.commit()
    print(" [PASS] Test cleanup: Restored clean state with 0 teams.")

    print("\n" + "=" * 80)
    print("ALL VERIFICATION SUITE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

if __name__ == "__main__":
    run_test_suite()
