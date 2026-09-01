import time
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.team import Team, TeamMember, TeamInvitation
from app.core.security import create_access_token

client = TestClient(app)

def run_all_cases():
    print("=" * 80)
    print("RIGOROUS VERIFICATION OF TWO-USER HEX BRIDGE FLOW & TEAM LIFECYCLE")
    print("=" * 80)

    db = SessionLocal()

    # Step 0: Ensure Sujal Sahu (#19) and Somadutta Sahu (#22) exist
    sujal = db.query(Student).filter(Student.id == 19).first()
    if not sujal:
        sujal = db.query(Student).filter(Student.name.ilike("%sujal sahu%")).first()
    soma = db.query(Student).filter(Student.id == 22).first()
    if not soma:
        soma = db.query(Student).filter(Student.name.ilike("%somadutta sahu%")).first()

    assert sujal is not None, "Sujal Sahu record must exist"
    assert soma is not None, "Somadutta Sahu record must exist"

    print(f"[OK] Verified Students: Sujal Sahu (#{sujal.id}), Somadutta Sahu (#{soma.id})")

    # ----------------------------------------------------
    # CASE 1 - 5: Login as Sujal Sahu & Open My Team
    # ----------------------------------------------------
    print("\n--- CASE 1 - 5: Sujal Sahu Session ---")
    # 1. Login as Sujal Sahu
    login_sujal = client.post("/api/students/login", json={
        "name": sujal.name,
        "password": "skillbridge2026",
        "mode": "login"
    })
    assert login_sujal.status_code == 200, f"Login failed for Sujal: {login_sujal.text}"
    token_sujal = login_sujal.json()["token"]
    headers_sujal = {"Authorization": f"Bearer {token_sujal}"}
    print(" [PASS] 1. Logged in as Sujal Sahu (Authenticated token acquired)")

    # 2. Open My Team
    resp_sujal = client.get("/api/teams/my", headers=headers_sujal)
    assert resp_sujal.status_code == 200
    teams_sujal = resp_sujal.json()
    print(" [PASS] 2. Opened My Team via /api/teams/my")

    # 3. Confirm HEX BRIDGE is shown
    hex_team_sujal = next((t for t in teams_sujal if "hex bridge" in t["name"].lower()), None)
    assert hex_team_sujal is not None, "HEX BRIDGE must be returned for Sujal Sahu"
    assert hex_team_sujal["id"] == 16
    print(f" [PASS] 3. Confirmed HEX BRIDGE is shown: Team #{hex_team_sujal['id']} '{hex_team_sujal['name']}'")

    # 4. Confirm Sujal Sahu is Team Leader
    sujal_member = next((m for m in hex_team_sujal["members"] if m["student_id"] == sujal.id), None)
    assert sujal_member is not None
    assert sujal_member["role"] == "Team Leader", f"Expected Sujal to be Team Leader, got {sujal_member['role']}"
    assert hex_team_sujal["creator_id"] == sujal.id
    print(f" [PASS] 4. Confirmed Sujal Sahu is Team Leader (Creator ID: {hex_team_sujal['creator_id']}, Member Role: '{sujal_member['role']}')")

    # 5. Confirm Somadutta Sahu is an accepted team member
    soma_member_for_sujal = next((m for m in hex_team_sujal["members"] if m["student_id"] == soma.id), None)
    assert soma_member_for_sujal is not None
    assert soma_member_for_sujal["status"] == "joined", f"Expected status 'joined', got {soma_member_for_sujal['status']}"
    print(f" [PASS] 5. Confirmed Somadutta Sahu is an accepted team member (Status: '{soma_member_for_sujal['status']}', Role: '{soma_member_for_sujal['role']}')")

    # ----------------------------------------------------
    # CASE 6 - 10: Login as Somadutta Sahu (Separate Session)
    # ----------------------------------------------------
    print("\n--- CASE 6 - 10: Somadutta Sahu Session ---")
    # 6. Login as Somadutta Sahu using a separate session
    login_soma = client.post("/api/students/login", json={
        "name": soma.name,
        "password": "skillbridge2026",
        "mode": "login"
    })
    assert login_soma.status_code == 200, f"Login failed for Somadutta: {login_soma.text}"
    token_soma = login_soma.json()["token"]
    headers_soma = {"Authorization": f"Bearer {token_soma}"}
    print(" [PASS] 6. Logged in as Somadutta Sahu via separate session (Different JWT)")

    # 7. Open My Team
    resp_soma = client.get("/api/teams/my", headers=headers_soma)
    assert resp_soma.status_code == 200
    teams_soma = resp_soma.json()
    print(" [PASS] 7. Opened My Team via /api/teams/my for Somadutta")

    # 8. Confirm HEX BRIDGE is also shown
    hex_team_soma = next((t for t in teams_soma if "hex bridge" in t["name"].lower()), None)
    assert hex_team_soma is not None, "HEX BRIDGE must be returned for Somadutta"
    assert hex_team_soma["id"] == hex_team_sujal["id"], "Both users MUST receive the exact same team ID"
    print(f" [PASS] 8. Confirmed HEX BRIDGE is also shown for Somadutta: Team #{hex_team_soma['id']} '{hex_team_soma['name']}'")

    # 9. Confirm Somadutta Sahu is shown as Team Member
    soma_member = next((m for m in hex_team_soma["members"] if m["student_id"] == soma.id), None)
    assert soma_member is not None
    assert soma_member["status"] == "joined"
    print(f" [PASS] 9. Confirmed Somadutta Sahu is shown as Team Member (Status: '{soma_member['status']}', Role: '{soma_member['role']}')")

    # 10. Confirm Sujal Sahu is shown as Team Leader
    sujal_member_for_soma = next((m for m in hex_team_soma["members"] if m["student_id"] == sujal.id), None)
    assert sujal_member_for_soma is not None
    assert sujal_member_for_soma["role"] == "Team Leader"
    assert hex_team_soma["creator_id"] == sujal.id
    print(f" [PASS] 10. Confirmed Sujal Sahu is shown as Team Leader to Somadutta (Role: '{sujal_member_for_soma['role']}', Creator: '{hex_team_soma['creator_name']}')")

    # ----------------------------------------------------
    # CASE 11 - 13: Refresh, Logout, Login Again
    # ----------------------------------------------------
    print("\n--- CASE 11 - 13: Persistence Across Page Refresh, Logout, & Relogin ---")
    # 11. Refresh simulation: Re-query database directly via fresh API calls
    refreshed_sujal = client.get("/api/teams/my", headers=headers_sujal).json()
    refreshed_soma = client.get("/api/teams/my", headers=headers_soma).json()
    assert any(t["id"] == 16 for t in refreshed_sujal)
    assert any(t["id"] == 16 for t in refreshed_soma)
    print(" [PASS] 11. Page refresh simulation: HEX BRIDGE persists across independent HTTP requests")

    # 12 & 13. Logout & re-login
    relogin_sujal = client.post("/api/students/login", json={"name": sujal.name, "password": "skillbridge2026", "mode": "login"})
    relogin_soma = client.post("/api/students/login", json={"name": soma.name, "password": "skillbridge2026", "mode": "login"})
    assert relogin_sujal.status_code == 200 and relogin_soma.status_code == 200
    fresh_sujal_team = client.get("/api/teams/my", headers={"Authorization": f"Bearer {relogin_sujal.json()['token']}"}).json()
    fresh_soma_team = client.get("/api/teams/my", headers={"Authorization": f"Bearer {relogin_soma.json()['token']}"}).json()
    assert any(t["id"] == 16 for t in fresh_sujal_team)
    assert any(t["id"] == 16 for t in fresh_soma_team)
    print(" [PASS] 12 & 13. Logout & Re-login: HEX BRIDGE still appears identically for both users")

    # ----------------------------------------------------
    # INVITATION ACCEPTANCE LIFECYCLE
    # ----------------------------------------------------
    print("\n--- INVITATION LIFECYCLE: A invites B -> B accepts -> Shared Team ---")
    # A (Sujal) invites B (Aarav Sharma #2) to HEX BRIDGE
    aarav = db.query(Student).filter(Student.id == 2).first()
    token_aarav = create_access_token(aarav.id)
    headers_aarav = {"Authorization": f"Bearer {token_aarav}"}

    invite_payload = {
        "recipient_id": aarav.id,
        "role": "AI/ML Developer",
        "message": "Please join HEX BRIDGE as our AI specialist!",
    }
    send_resp = client.post(f"/api/teams/16/invitations", json=invite_payload, headers=headers_sujal)
    assert send_resp.status_code in [200, 201], f"Failed to send invite: {send_resp.text}"
    inv_data = send_resp.json()
    inv_id = inv_data["id"]
    print(f" [PASS] A (Sujal) sent invitation #{inv_id} to B (Aarav) for role 'AI/ML Developer'")

    # B (Aarav) receives notification
    pending_resp = client.get("/api/teams/invitations/pending", headers=headers_aarav)
    assert pending_resp.status_code == 200
    pending_invs = pending_resp.json()
    assert any(i["id"] == inv_id for i in pending_invs), "Invitation must appear in B's pending notifications"
    print(f" [PASS] B (Aarav) received notification for invitation #{inv_id}")

    # B (Aarav) accepts
    accept_resp = client.post(f"/api/teams/invitations/{inv_id}/accept", headers=headers_aarav)
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "ACCEPTED"
    print(f" [PASS] B (Aarav) accepted invitation #{inv_id}")

    # A (Sujal) sees B (Aarav) as accepted member in HEX BRIDGE
    a_team_check = client.get("/api/teams/my", headers=headers_sujal).json()
    hex_a = next(t for t in a_team_check if t["id"] == 16)
    assert any(m["student_id"] == aarav.id and m["status"] == "joined" for m in hex_a["members"])
    print(" [PASS] A (Sujal) sees B (Aarav) as accepted member in HEX BRIDGE roster")

    # B (Aarav) sees A and HEX BRIDGE in My Team
    b_team_check = client.get("/api/teams/my", headers=headers_aarav).json()
    hex_b = next(t for t in b_team_check if t["id"] == 16)
    assert hex_b["name"] == "HEX BRIDGE"
    assert hex_b["creator_id"] == sujal.id
    assert any(m["student_id"] == sujal.id for m in hex_b["members"])
    print(f" [PASS] B (Aarav) sees HEX BRIDGE (created by Sujal Sahu) in his own My Team page")

    # ----------------------------------------------------
    # INVITATION REJECTION LIFECYCLE
    # ----------------------------------------------------
    print("\n--- INVITATION LIFECYCLE: A invites C -> C rejects -> Not a Member ---")
    # A (Sujal) invites C (Aditya Mishra #3)
    aditya = db.query(Student).filter(Student.id == 3).first()
    token_aditya = create_access_token(aditya.id)
    headers_aditya = {"Authorization": f"Bearer {token_aditya}"}

    invite_c = {
        "recipient_id": aditya.id,
        "role": "Frontend Specialist",
        "message": "Join us on HEX BRIDGE",
    }
    send_c_resp = client.post("/api/teams/16/invitations", json=invite_c, headers=headers_sujal)
    assert send_c_resp.status_code in [200, 201]
    inv_c_id = send_c_resp.json()["id"]
    print(f" [PASS] A (Sujal) sent invitation #{inv_c_id} to C (Aditya)")

    # C rejects
    reject_resp = client.post(f"/api/teams/invitations/{inv_c_id}/reject", headers=headers_aditya)
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"
    print(f" [PASS] C (Aditya) rejected invitation #{inv_c_id}")

    # Confirm C is NOT a member of HEX BRIDGE
    final_hex = client.get("/api/teams/my", headers=headers_sujal).json()
    hex_now = next(t for t in final_hex if t["id"] == 16)
    assert not any(m["student_id"] == aditya.id for m in hex_now["members"]), "Rejected candidate must NOT be a member"
    print(" [PASS] Confirmed: C (Aditya) does NOT appear as a team member of HEX BRIDGE")

    # Cleanup temporary test memberships and test invitations to preserve HEX BRIDGE with strictly Sujal & Somadutta
    db.query(TeamMember).filter(TeamMember.team_id == 16, TeamMember.student_id == aarav.id).delete()
    db.query(TeamInvitation).filter(TeamInvitation.id.in_([inv_id, inv_c_id])).delete()
    db.commit()
    print(" [PASS] Test cleanup: HEX BRIDGE team restored strictly to original members Sujal & Somadutta.")

    print("\n" + "=" * 80)
    print("ALL 13 CASES & LIFECYCLE TESTS PASSED WITH 100% ACCURACY!")
    print("=" * 80)

if __name__ == "__main__":
    run_all_cases()
