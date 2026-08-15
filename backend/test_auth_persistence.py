"""
Comprehensive Authentication and State Persistence Test Suite for SkillBridge.

Tests:
- TEST 1: New user registration & login with password, token generation, data persistence.
- TEST 2: Progress persistence & state resumption (navigating to 'passport', submitting evidence, relogging in and resuming 'passport').
- TEST 3: Security: Incorrect password rejection with HTTP 401 and clear error message.
- TEST 4: Isolation: Multi-user isolation (User A vs User B data boundaries).
- TEST 5: Backward compatibility: Existing SkillBridge endpoints (Admin, Skills, Evidence, Teams, Recommendations) work seamlessly.
"""

import sys
import json
import urllib.request
import urllib.error
import time

BASE_URL = "http://127.0.0.1:8000/api"


def http_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data is not None:
        encoded = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    else:
        encoded = None

    req = urllib.request.Request(url, data=encoded, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = body
        return e.code, parsed


def run_auth_and_persistence_tests():
    print("=" * 70)
    print("SKILLBRIDGE AUTHENTICATION & PERSISTENCE VERIFICATION SUITE")
    print("=" * 70)

    # 1. Health check
    status, health_data = http_request(f"{BASE_URL}/health")
    assert status == 200, f"Health check failed: {health_data}"
    print("[PASS] 1. Backend API is online and healthy.")

    timestamp = int(time.time())
    user_a_name = f"TestUserAlpha_{timestamp}"
    user_a_password = "SecurePasswordAlpha123!"
    user_b_name = f"TestUserBeta_{timestamp}"
    user_b_password = "SecurePasswordBeta456!"

    # =========================================================================
    # TEST 1: New user registration, login, token generation & data persistence
    # =========================================================================
    print("\n--- TEST 1: New User Registration & Login ---")
    status, res_a = http_request(
        f"{BASE_URL}/students/login",
        method="POST",
        data={"name": user_a_name, "password": user_a_password, "mode": "register"},
    )
    assert status == 200, f"Registration failed ({status}): {res_a}"
    assert "token" in res_a, "Missing auth token in response"
    assert res_a["student"]["name"] == user_a_name, "Student name mismatch"
    assert res_a["last_screen"] == "dashboard", "Initial last_screen should be 'dashboard'"
    user_a_id = res_a["student"]["id"]
    print(f"[PASS] TEST 1.1: User '{user_a_name}' registered successfully (ID: {user_a_id}).")

    # Re-login with the same credentials
    status, relogin_a = http_request(
        f"{BASE_URL}/students/login",
        method="POST",
        data={"name": user_a_name, "password": user_a_password, "mode": "login"},
    )
    assert status == 200, f"Re-login failed: {relogin_a}"
    assert relogin_a["student"]["id"] == user_a_id, "Student ID changed across logins"
    print(f"[PASS] TEST 1.2: Re-login recognized existing account and restored profile.")

    # =========================================================================
    # TEST 2: User makes progress -> State & evidence restored upon login
    # =========================================================================
    print("\n--- TEST 2: State Resumption & Evidence Persistence ---")
    # Step 2a: Update user navigation state to 'passport'
    status, state_res = http_request(
        f"{BASE_URL}/students/{user_a_id}/state",
        method="PATCH",
        data={"last_screen": "passport", "last_state_json": json.dumps({"step": 2, "activeTab": "verified"})},
    )
    assert status == 200, f"Update state failed: {state_res}"
    assert state_res["last_screen"] == "passport", "State last_screen was not updated"
    print("[PASS] TEST 2.1: Navigation state updated to 'passport'.")

    # Step 2b: Submit evidence for User A
    status, ev_res = http_request(
        f"{BASE_URL}/evidence",
        method="POST",
        data={
            "student_id": user_a_id,
            "skill_id": 1,  # Python
            "evidence_type": "project",
            "title": "Alpha Distributed Microservice",
            "description": "High-concurrency async Python project.",
            "issuer": "GitHub Portfolio",
            "evidence_url": "https://github.com/test-alpha/microservice",
        },
    )
    assert status == 201, f"Evidence submission failed: {ev_res}"
    print(f"[PASS] TEST 2.2: Evidence submitted for User A (Evidence ID: {ev_res['id']}).")

    # Step 2c: Simulate user closing website and logging in again later
    status, resume_login = http_request(
        f"{BASE_URL}/students/login",
        method="POST",
        data={"name": user_a_name, "password": user_a_password, "mode": "login"},
    )
    assert status == 200, f"Resume login failed: {resume_login}"
    assert resume_login["last_screen"] == "passport", f"Expected last_screen 'passport', got {resume_login['last_screen']}"
    assert len(resume_login["student"]["evidence"]) >= 1, "User evidence was not restored upon login"
    assert resume_login["student"]["evidence"][0]["title"] == "Alpha Distributed Microservice"
    print(f"[PASS] TEST 2.3: Re-login automatically returned user to exact 'passport' screen with restored evidence.")

    # =========================================================================
    # TEST 3: Security: Wrong password rejection
    # =========================================================================
    print("\n--- TEST 3: Password Security & Rejection ---")
    status, wrong_pw_res = http_request(
        f"{BASE_URL}/students/login",
        method="POST",
        data={"name": user_a_name, "password": "WrongPasswordXYZ123!"},
    )
    assert status == 401, f"Expected 401 Unauthorized for wrong password, got {status}"
    assert "Incorrect password" in str(wrong_pw_res), f"Expected clear error message, got: {wrong_pw_res}"
    print(f"[PASS] TEST 3: Incorrect password was properly rejected with HTTP 401: {wrong_pw_res['detail']}.")

    # =========================================================================
    # TEST 4: Multi-user isolation
    # =========================================================================
    print("\n--- TEST 4: Multi-User Isolation ---")
    # Register User B
    status, res_b = http_request(
        f"{BASE_URL}/students/login",
        method="POST",
        data={"name": user_b_name, "password": user_b_password, "mode": "register"},
    )
    assert status == 200, f"User B registration failed: {res_b}"
    user_b_id = res_b["student"]["id"]
    assert user_b_id != user_a_id, "User B received User A's student ID"
    assert len(res_b["student"]["evidence"]) == 0, "User B should start with 0 evidence items"
    print(f"[PASS] TEST 4.1: User B ({user_b_name}) registered with clean isolation (0 evidence items).")

    # Verify User A's data is still intact
    status, fetch_a = http_request(f"{BASE_URL}/students/{user_a_id}")
    assert status == 200
    assert len(fetch_a["evidence"]) == 1
    assert fetch_a["evidence"][0]["title"] == "Alpha Distributed Microservice"
    print(f"[PASS] TEST 4.2: User A's private evidence is completely isolated from User B.")

    # =========================================================================
    # TEST 5: Existing SkillBridge features continue working seamlessly
    # =========================================================================
    print("\n--- TEST 5: Full Regression Testing on Existing Features ---")
    # 5.1 Admin queue check
    status, queue = http_request(f"{BASE_URL}/admin/evidence/pending")
    assert status == 200, f"Admin queue retrieval failed: {queue}"
    print(f"[PASS] 5.1: Admin evidence queue is operational ({len(queue)} items).")

    # 5.2 Admin approve User A's evidence
    status, approve_res = http_request(
        f"{BASE_URL}/admin/evidence/{ev_res['id']}/approve",
        method="POST",
        headers={"Authorization": "Bearer admin-session-token-sujal-verified"},
    )
    assert status == 200, f"Admin evidence approval failed: {approve_res}"
    print(f"[PASS] 5.2: Admin evidence approval succeeded.")

    # 5.3 Verify User A's verified skill
    status, fetch_a_updated = http_request(f"{BASE_URL}/students/{user_a_id}")
    assert status == 200
    assert len(fetch_a_updated["skills"]) >= 1, "Verified skill was not synchronized"
    assert fetch_a_updated["skills"][0]["verification_status"] == "verified"
    print(f"[PASS] 5.3: StudentSkill automatically synchronized to 'verified'.")

    # 5.4 Internship recommendations
    status, recs = http_request(f"{BASE_URL}/recommendations/students/{user_a_id}")
    assert status == 200, f"Recommendations failed: {recs}"
    assert "recommendations" in recs
    print(f"[PASS] 5.4: Explainable internship recommendations operational ({len(recs['recommendations'])} internships).")

    # 5.5 Team builder candidates
    status, teams = http_request(f"{BASE_URL}/teams")
    assert status == 200
    if len(teams) > 0:
        team_id = teams[0]["id"]
        status, candidates = http_request(f"{BASE_URL}/teams/{team_id}/candidates")
        assert status == 200
        print(f"[PASS] 5.5: Team candidate explainable recommendations operational ({len(candidates)} candidates).")

    print("\n" + "=" * 70)
    print("ALL AUTHENTICATION & PERSISTENCE TESTS PASSED FLAWLESSLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_auth_and_persistence_tests()
