import os
import sys

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student


def run_auth_lifecycle_test():
    print("=" * 80)
    print("SKILLBRIDGE AUTH LIFECYCLE & MULTI-ACCOUNT VERIFICATION TEST")
    print("=" * 80)

    client = TestClient(app)
    db = SessionLocal()

    # 1. API Health Check (both /api/health and /health)
    print("\n--- 1. API Health Check ---")
    h1 = client.get("/api/health")
    assert h1.status_code == 200, f"/api/health failed: {h1.text}"
    print(f" [PASS] /api/health responded: {h1.json()['status']} ({h1.json()['db_dialect']})")

    h2 = client.get("/health")
    assert h2.status_code == 200, f"/health failed: {h2.text}"
    print(f" [PASS] /health responded: {h2.json()['status']}")

    # 2. Signup Account 1
    print("\n--- 2. Signup Account 1 (Alice Kumar) ---")
    alice_name = "Alice Kumar"
    alice_pass = "alicePass2026"
    reg_alice = client.post("/api/students/login", json={
        "name": alice_name,
        "password": alice_pass,
        "confirm_password": alice_pass,
        "mode": "register",
    })
    assert reg_alice.status_code == 200, f"Alice registration failed: {reg_alice.text}"
    alice_data = reg_alice.json()
    alice_id = alice_data["student"]["id"]
    alice_token = alice_data["token"]
    print(f" [PASS] Alice registered with ID #{alice_id}, token issued.")

    # Verify Alice Profile
    me_alice = client.get("/api/students/me", headers={"Authorization": f"Bearer {alice_token}"})
    assert me_alice.status_code == 200
    assert me_alice.json()["name"] == alice_name
    print(f" [PASS] /api/students/me confirms Alice Kumar profile.")

    # 3. Signup Account 2
    print("\n--- 3. Signup Account 2 (Bob Sen) ---")
    bob_name = "Bob Sen"
    bob_pass = "bobPass2026"
    reg_bob = client.post("/api/students/login", json={
        "name": bob_name,
        "password": bob_pass,
        "confirm_password": bob_pass,
        "mode": "register",
    })
    assert reg_bob.status_code == 200, f"Bob registration failed: {reg_bob.text}"
    bob_data = reg_bob.json()
    bob_id = bob_data["student"]["id"]
    bob_token = bob_data["token"]
    print(f" [PASS] Bob registered with ID #{bob_id}, token issued.")

    # Verify Bob Profile
    me_bob = client.get("/api/students/me", headers={"Authorization": f"Bearer {bob_token}"})
    assert me_bob.status_code == 200
    assert me_bob.json()["name"] == bob_name
    print(f" [PASS] /api/students/me confirms Bob Sen profile.")

    # 4. Confirm complete separation between Alice and Bob
    assert alice_id != bob_id, "Accounts must have distinct IDs"
    assert me_alice.json()["name"] != me_bob.json()["name"]
    print(f" [PASS] Separate accounts confirmed: Alice (#{alice_id}) vs Bob (#{bob_id}).")

    # 5. Logout & Login again with Account 1 (Alice)
    print("\n--- 4. Logout & Login Again (Alice) ---")
    # Simulate fresh login with same password
    relogin_alice = client.post("/api/students/login", json={
        "name": alice_name,
        "password": alice_pass,
        "mode": "login",
    })
    assert relogin_alice.status_code == 200, f"Alice relogin failed: {relogin_alice.text}"
    new_alice_token = relogin_alice.json()["token"]
    alice_check = client.get("/api/students/me", headers={"Authorization": f"Bearer {new_alice_token}"})
    assert alice_check.status_code == 200
    assert alice_check.json()["id"] == alice_id
    print(f" [PASS] Alice successfully logged back in with same password. ID preserved: #{alice_id}.")

    # 6. Wrong Password Rejection
    print("\n--- 5. Wrong Password Rejection ---")
    bad_pass_resp = client.post("/api/students/login", json={
        "name": alice_name,
        "password": "WrongPassword999!",
        "mode": "login",
    })
    assert bad_pass_resp.status_code == 401
    assert bad_pass_resp.json()["detail"] == "Invalid password."
    print(" [PASS] Incorrect password correctly rejected with 401 'Invalid password.'")

    # 7. Logout & Login again with Account 2 (Bob)
    print("\n--- 6. Logout & Login Again (Bob) ---")
    relogin_bob = client.post("/api/students/login", json={
        "name": bob_name,
        "password": bob_pass,
        "mode": "login",
    })
    assert relogin_bob.status_code == 200, f"Bob relogin failed: {relogin_bob.text}"
    new_bob_token = relogin_bob.json()["token"]
    bob_check = client.get("/api/students/me", headers={"Authorization": f"Bearer {new_bob_token}"})
    assert bob_check.status_code == 200
    assert bob_check.json()["id"] == bob_id
    print(f" [PASS] Bob successfully logged back in with same password. ID preserved: #{bob_id}.")

    # 8. Demo Account Login (Arjun Patel)
    print("\n--- 7. Canonical Demo Account Verification (Arjun Patel) ---")
    demo_login = client.post("/api/students/login", json={
        "name": "Arjun Patel",
        "password": "skillbridge2026",
        "mode": "login",
    })
    assert demo_login.status_code == 200, f"Demo login failed: {demo_login.text}"
    assert demo_login.json()["student"]["name"] == "Arjun Patel"
    print(f" [PASS] Demo account Arjun Patel logged in successfully.")

    # 9. Clean up test users
    db.query(Student).filter(Student.id.in_([alice_id, bob_id])).delete()
    db.commit()
    print("\n [PASS] Test cleanup: Purged temporary accounts Alice and Bob.")

    print("\n" + "=" * 80)
    print("ALL AUTH LIFECYCLE & MULTI-ACCOUNT TESTS PASSED (100% SUCCESS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_auth_lifecycle_test()
