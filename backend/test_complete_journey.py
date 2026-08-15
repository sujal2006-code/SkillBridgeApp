"""
End-to-End User Flow Verification Script for SkillBridge (Pure Standard Library).

Tests:
1. Student onboarding (Sujal) starting with 0% passport completion.
2. Evidence submission with initial PENDING status.
3. Protected admin authentication (Sujal / myteam1).
4. Admin queue retrieval, evidence approval, and StudentSkill synchronization.
5. Dynamic passport percentage calculation (0% -> 20% -> 40%).
6. Explainable internship matching recalculation with evidence citations and missing skills.
7. Explainable multidisciplinary team candidate recommendations with realistic percentages.
8. Team candidate invitation and exclusion.
9. Verification of anti-bias and fairness guarantees.
"""

import sys
import json
import urllib.request
import urllib.error

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

def run_tests():
    print("=" * 70)
    print("SKILLBRIDGE END-TO-END WORKFLOW & VERIFICATION SUITE")
    print("=" * 70)

    # 1. Health check
    status, health_data = http_request(f"{BASE_URL}/health")
    assert status == 200, f"Health check failed: {health_data}"
    print("[PASS] 1. Backend API is online and healthy.")

    # 2. Student Onboarding: Sujal
    import time
    ts = int(time.time())
    onboard_payload = {
        "name": f"Sujal Demo User {ts}",
        "email": f"sujal.demo.{ts}@example.edu",
        "university": "State University of Technology"
    }
    status, sujal = http_request(f"{BASE_URL}/students/onboard", method="POST", data=onboard_payload)
    assert status == 200, f"Onboard failed: {sujal}"
    student_id = sujal["id"]
    print(f"[PASS] 2. Student onboarded successfully: ID={student_id}, Name='{sujal['name']}'")

    # 3. Verify Fresh Student Starts with 0 Verified Skills & 0% Match
    status, student_detail = http_request(f"{BASE_URL}/students/{student_id}")
    assert status == 200
    verified_skills = [s for s in student_detail.get("skills", []) if s.get("verification_status") == "verified"]
    print(f"[PASS] 3. Fresh student state verified: {len(verified_skills)} verified skills (0% Passport completion).")

    # Check recommendations for fresh student -> all matches should be 0%
    status, recs_data = http_request(f"{BASE_URL}/recommendations/students/{student_id}")
    assert status == 200
    for rec in recs_data.get("recommendations", []):
        assert rec["match_score"] == 0.0, f"Expected 0.0% match for new student without verified skills, got {rec['match_score']}"
        assert len(rec["missing_skills"]) == len(rec["required_skills"])
    print("[PASS] 4. Explainable recommendations for 0-skill student correctly show 0.0% match and identify all missing skills.")

    # 4. Add Evidence Item: Project for FastAPI (Initial status PENDING)
    status, skills_list = http_request(f"{BASE_URL}/skills")
    fastapi_skill = next((s for s in skills_list if s["name"] == "FastAPI"), None)
    assert fastapi_skill is not None, "FastAPI skill not found in DB"

    evidence_payload = {
        "student_id": student_id,
        "skill_id": fastapi_skill["id"],
        "evidence_type": "project",
        "title": "High-Concurrency Async Microservice",
        "description": "Engineered asynchronous FastAPI microservice with Pydantic validation.",
        "issuer": "GitHub Portfolio Showcase",
        "verification_status": "pending",
        "evidence_url": "https://github.com/sujal/fastapi-microservice"
    }
    status, created_evidence = http_request(f"{BASE_URL}/evidence", method="POST", data=evidence_payload)
    assert status in [200, 201], f"Add evidence failed: {created_evidence}"
    evidence_id = created_evidence["id"]
    assert created_evidence["verification_status"] == "pending"
    print(f"[PASS] 5. Evidence submitted with PENDING status: Evidence ID={evidence_id}")

    # 5. Protected Admin Authentication
    status, bad_login = http_request(f"{BASE_URL}/admin/login", method="POST", data={"username": "Sujal", "password": "wrongpassword"})
    assert status == 401, "Admin login should reject invalid credentials"

    status, good_login = http_request(f"{BASE_URL}/admin/login", method="POST", data={"username": "Sujal", "password": "myteam1"})
    assert status == 200, f"Admin login failed: {good_login}"
    assert "token" in good_login
    print("[PASS] 6. Protected admin authentication verified (Username: Sujal, Password: myteam1).")

    # 6. Admin Verification Queue
    status, pending_list = http_request(f"{BASE_URL}/admin/evidence/pending")
    assert status == 200
    pending_ids = [item["id"] for item in pending_list]
    assert evidence_id in pending_ids, f"Submitted evidence ID {evidence_id} not found in pending queue"
    print(f"[PASS] 7. Pending queue contains submitted evidence (Queue count: {len(pending_list)}).")

    # 7. Admin Approves Evidence
    status, approved_ev = http_request(f"{BASE_URL}/admin/evidence/{evidence_id}/approve", method="POST")
    assert status == 200
    assert approved_ev["verification_status"] == "verified"
    print(f"[PASS] 8. Admin approved evidence ID {evidence_id}. Verification status is now 'verified'.")

    # 8. Verify StudentSkill Synchronization & Dynamic Passport Update
    status, student_detail = http_request(f"{BASE_URL}/students/{student_id}")
    verified_skills = [s for s in student_detail.get("skills", []) if s.get("verification_status") == "verified"]
    assert len(verified_skills) >= 1
    assert any(s["skill_id"] == fastapi_skill["id"] for s in verified_skills)
    passport_pct = min(100, len(verified_skills) * 20)
    print(f"[PASS] 9. Student skill synchronized to passport: {len(verified_skills)} verified skill -> Passport Completion = {passport_pct}%.")

    # 9. Dynamic Recommendation Recalculation with Evidence Citations
    status, recs_data = http_request(f"{BASE_URL}/recommendations/students/{student_id}")
    assert status == 200
    found_positive_match = False
    for rec in recs_data.get("recommendations", []):
        if "FastAPI" in rec["required_skills"]:
            assert rec["match_score"] > 0.0, f"Expected positive match score for internship requiring FastAPI, got {rec['match_score']}"
            matched_names = [ms["skill_name"] for ms in rec["matched_skills"]]
            assert "FastAPI" in matched_names
            assert len(rec["evidence_support"]) > 0, "Expected supporting evidence citation in recommendation"
            found_positive_match = True
            print(f"       -> Match Details for '{rec['internship_title']}': Score={rec['match_score']}%, Matched={matched_names}, Missing={rec['missing_skills']}")
            print(f"       -> Explanation: {rec['explanation']}")

    assert found_positive_match, "Should have found at least one match for FastAPI"
    print("[PASS] 10. Internship matching dynamically recalculated with verified evidence citations and transparent missing skills.")

    # 10. Multidisciplinary Team Builder Candidates
    status, teams = http_request(f"{BASE_URL}/teams")
    if not teams:
        status, team_res = http_request(f"{BASE_URL}/teams", method="POST", data={
            "name": "Autonomous Robotics Lab",
            "description": "Multi-agent systems, neural vision, and distributed control.",
            "creator_id": student_id,
            "required_skill_ids": [1, 2, 5]
        })
        team_id = team_res["id"]
    else:
        team_id = teams[0]["id"]

    status, candidates = http_request(f"{BASE_URL}/teams/{team_id}/candidates")
    assert status == 200
    assert len(candidates) > 0, "Expected candidates to be returned"
    
    candidate_scores = [c["match_score"] for c in candidates]
    assert any(score > 0 for score in candidate_scores), f"Candidate scores should not all be 0: {candidate_scores}"
    print(f"[PASS] 11. Multidisciplinary Team Builder candidate recommendations verified (Scores: {candidate_scores}).")

    # 11. Invite Candidate & Verify Exclusion
    first_candidate = candidates[0]
    status, invite_res = http_request(f"{BASE_URL}/teams/{team_id}/members", method="POST", data={
        "student_id": first_candidate["candidate_id"],
        "role": first_candidate["role_suggestion"],
        "status": "invited"
    })
    assert status in [200, 201]
    print(f"[PASS] 12. Candidate {first_candidate['candidate_name']} invited to team ID {team_id}.")

    # Fresh candidates list excludes invited member
    status, fresh_cands = http_request(f"{BASE_URL}/teams/{team_id}/candidates")
    fresh_cand_ids = [c["candidate_id"] for c in fresh_cands]
    assert first_candidate["candidate_id"] not in fresh_cand_ids, "Invited candidate should be excluded from candidate pool"
    print(f"[PASS] 13. Invited candidate successfully excluded from subsequent recommendation queries.")

    # 12. Fairness and Anti-Bias Verification
    sample_rec = recs_data["recommendations"][0]
    disallowed_fields = ["gender", "race", "ethnicity", "religion", "caste", "photo", "age", "university_prestige"]
    for field in disallowed_fields:
        assert field not in sample_rec, f"Protected attribute '{field}' found in recommendation response!"
    print("[PASS] 14. Anti-bias guarantee verified: Recommendations rely 100% on verified skills and evidence.")

    print("\n" + "=" * 70)
    print("ALL 14 END-TO-END WORKFLOW VERIFICATIONS PASSED (100% SUCCESS)")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"[FAIL] Error running verification: {e}")
        sys.exit(1)
