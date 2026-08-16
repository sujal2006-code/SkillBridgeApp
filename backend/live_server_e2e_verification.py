import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def post_json(path, data, token=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def get_json(path, token=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def run_verification():
    print("==================================================")
    print("LIVE PRODUCTION SERVER E2E HTTP VERIFICATION")
    print("==================================================")

    # 1. Health Check
    status, health = get_json("/api/health")
    assert status == 200 and health["status"] == "ok"
    print(f"[LIVE PASS] 1. Backend Server is LIVE: {health}")

    ts = int(time.time() * 1000)
    user_1_name = f"Aarav_Sharma_{ts}"
    user_1_pwd = "PasswordA1"
    user_2_name = f"Priya_Patel_{ts}"
    user_2_pwd = "PasswordB2"

    # 2. Register User 1
    status, reg1 = post_json("/api/students/login", {
        "name": user_1_name,
        "password": user_1_pwd,
        "confirm_password": user_1_pwd,
        "mode": "register"
    })
    assert status == 200
    user_1_id = reg1["student"]["id"]
    token_1 = reg1["token"]
    print(f"[LIVE PASS] 2. User 1 '{user_1_name}' registered successfully (ID: {user_1_id}).")

    # 3. User 1 submits Evidence
    status, ev1 = post_json("/api/evidence", {
        "title": "Distributed ML Pipeline on GKE",
        "description": "PyTorch distributed training with Ray.",
        "evidence_type": "project",
        "issuer": "Stanford AI Lab",
        "verification_status": "pending"
    }, token=token_1)
    assert status == 201
    assert ev1["student_id"] == user_1_id
    print(f"[LIVE PASS] 3. User 1 submitted evidence (Evidence ID: {ev1['id']}, Student ID: {ev1['student_id']}).")

    # 4. Fetch User 1 profile via token
    status, prof1 = get_json("/api/students/me", token=token_1)
    assert status == 200
    assert prof1["name"] == user_1_name
    assert len(prof1["evidence"]) == 1
    assert prof1["evidence"][0]["title"] == "Distributed ML Pipeline on GKE"
    print(f"[LIVE PASS] 4. User 1 profile verified via /api/students/me: {prof1['name']}, {len(prof1['evidence'])} evidence.")

    # 5. Register User 2
    status, reg2 = post_json("/api/students/login", {
        "name": user_2_name,
        "password": user_2_pwd,
        "confirm_password": user_2_pwd,
        "mode": "register"
    })
    assert status == 200
    user_2_id = reg2["student"]["id"]
    token_2 = reg2["token"]
    assert user_2_id != user_1_id
    print(f"[LIVE PASS] 5. User 2 '{user_2_name}' registered successfully (ID: {user_2_id}).")

    # 6. Verify User 2 has ZERO data from User 1
    status, prof2_initial = get_json("/api/students/me", token=token_2)
    assert status == 200
    assert prof2_initial["name"] == user_2_name
    assert len(prof2_initial["evidence"]) == 0
    print(f"[LIVE PASS] 6. User 2 initial profile verified: ZERO evidence from User 1.")

    # 7. User 2 submits Evidence
    status, ev2 = post_json("/api/evidence", {
        "title": "Fintech Microservices Engine",
        "description": "High-frequency event-driven trade processing system.",
        "evidence_type": "project",
        "issuer": "Fintech Guild",
        "verification_status": "pending"
    }, token=token_2)
    assert status == 201
    assert ev2["student_id"] == user_2_id
    print(f"[LIVE PASS] 7. User 2 submitted evidence (Evidence ID: {ev2['id']}, Student ID: {ev2['student_id']}).")

    # 8. Verify User 2 profile has ONLY User 2's evidence
    status, prof2 = get_json("/api/students/me", token=token_2)
    assert status == 200
    assert prof2["name"] == user_2_name
    assert len(prof2["evidence"]) == 1
    assert prof2["evidence"][0]["title"] == "Fintech Microservices Engine"
    print(f"[LIVE PASS] 8. User 2 profile verified: {prof2['name']}, {len(prof2['evidence'])} evidence.")

    # 9. Relogin User 1
    status, relogin1 = post_json("/api/students/login", {
        "name": user_1_name,
        "password": user_1_pwd,
        "mode": "login"
    })
    assert status == 200
    token_1_new = relogin1["token"]
    status, prof1_re = get_json("/api/students/me", token=token_1_new)
    assert status == 200
    assert prof1_re["name"] == user_1_name
    assert len(prof1_re["evidence"]) == 1
    assert prof1_re["evidence"][0]["title"] == "Distributed ML Pipeline on GKE"
    print(f"[LIVE PASS] 9. User 1 relogin verified: Name={prof1_re['name']}, Evidence={prof1_re['evidence'][0]['title']}.")

    # 10. Relogin User 2
    status, relogin2 = post_json("/api/students/login", {
        "name": user_2_name,
        "password": user_2_pwd,
        "mode": "login"
    })
    assert status == 200
    token_2_new = relogin2["token"]
    status, prof2_re = get_json("/api/students/me", token=token_2_new)
    assert status == 200
    assert prof2_re["name"] == user_2_name
    assert len(prof2_re["evidence"]) == 1
    assert prof2_re["evidence"][0]["title"] == "Fintech Microservices Engine"
    print(f"[LIVE PASS] 10. User 2 relogin verified: Name={prof2_re['name']}, Evidence={prof2_re['evidence'][0]['title']}.")

    print("==================================================")
    print("ALL 10 LIVE SERVER PRODUCTION VERIFICATIONS PASSED")
    print("==================================================")

if __name__ == "__main__":
    run_verification()
