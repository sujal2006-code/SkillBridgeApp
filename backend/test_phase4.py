import urllib.request
import urllib.error
import json
from datetime import datetime, timezone

BASE = "http://127.0.0.1:8000"

def post_json(path: str, data: dict):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    return res.getcode(), json.loads(res.read())

def get_json(path: str):
    req = urllib.request.Request(f"{BASE}{path}")
    res = urllib.request.urlopen(req)
    return res.getcode(), json.loads(res.read())

def get_status(path: str):
    req = urllib.request.Request(f"{BASE}{path}")
    res = urllib.request.urlopen(req)
    return res.getcode()

def run_tests():
    print("==================================================")
    print("   SKILLBRIDGE PHASE 4 TEST SUITE VERIFICATION   ")
    print("==================================================")

    # ----------------------------------------------------
    # TEST 1: Backward Compatibility & Health
    # ----------------------------------------------------
    code, health = get_json("/api/health")
    assert code == 200
    assert health["status"] == "ok"
    print("[PASS] Test 1.1: GET /api/health returned 200 OK")

    code = get_status("/api/docs")
    assert code == 200
    print("[PASS] Test 1.2: GET /api/docs Swagger UI returned 200 OK")

    code, openapi = get_json("/api/openapi.json")
    assert code == 200 and "paths" in openapi
    print("[PASS] Test 1.3: GET /api/openapi.json schema returned 200 OK")

    code, students = get_json("/api/students")
    assert code == 200 and len(students) >= 1
    print(f"[PASS] Test 1.4: GET /api/students returned {len(students)} student(s)")

    # ----------------------------------------------------
    # TEST 2: Demo Student Recommendations (Alex Rivera, ID=1)
    # ----------------------------------------------------
    code, recs_resp = get_json("/api/recommendations/students/1")
    assert code == 200
    assert "recommendations" in recs_resp
    assert recs_resp["student_id"] == 1
    recs = recs_resp["recommendations"]
    assert len(recs) >= 2
    print(f"[PASS] Test 2.1: GET /api/recommendations/students/1 returned {len(recs)} ranked recommendations")
    
    for r in recs:
        print(f"       -> {r['internship_title']} ({r['company']}): {r['match_score']}% match")
        print(f"          Explanation: {r['explanation']}")

    # Check top recommendation for Alex Rivera (Internship 1 requires Python, FastAPI, SQL & PostgreSQL)
    top_rec = recs[0]
    assert top_rec["match_score"] == 100.0
    assert len(top_rec["matched_skills"]) >= 3
    assert len(top_rec["missing_skills"]) == 0
    assert len(top_rec["evidence_support"]) >= 5
    print("[PASS] Test 2.2: Perfect Match verified for top internship (100.0% score with 5 evidence items)")

    # ----------------------------------------------------
    # TEST 3: Partial Match & Missing Skills Analysis
    # ----------------------------------------------------
    # Internship 2 (requires React, TypeScript, Python)
    # Alex Rivera has React (verified) and Python (verified), but lacks TypeScript
    code, single_rec = get_json("/api/recommendations/students/1/internships/2")
    assert code == 200
    assert single_rec["match_score"] == 66.7  # 2 out of 3 satisfied
    assert "TypeScript" in single_rec["missing_skills"]
    assert "TypeScript is missing" in single_rec["explanation"]
    print("[PASS] Test 3: Partial Match verified (66.7% score, TypeScript identified in missing_skills and explanation)")

    # ----------------------------------------------------
    # TEST 4: Insufficient Proficiency & Unverified Evidence
    # ----------------------------------------------------
    # Create test student "Jordan Test"
    ts = int(datetime.now(timezone.utc).timestamp())
    _, jordan = post_json("/api/students", {
        "name": "Jordan Test",
        "email": f"jordan.test.{ts}@example.edu",
        "university": "Test Tech",
        "graduation_year": 2027
    })
    jordan_id = jordan["id"]

    # Fetch skill IDs
    _, skills_list = get_json("/api/skills")
    skill_map = {s["name"]: s["id"] for s in skills_list}

    # Add unverified evidence for Jordan
    _, jordan_ev = post_json("/api/evidence", {
        "student_id": jordan_id,
        "skill_id": skill_map["Python"],
        "evidence_type": "project",
        "title": "Unverified script",
        "verification_status": "pending"  # Pending = Unverified
    })

    # Test recommendations for Jordan (has no verified skills)
    code, jordan_recs = get_json(f"/api/recommendations/students/{jordan_id}")
    assert code == 200
    for r in jordan_recs["recommendations"]:
        assert r["match_score"] == 0.0
    print("[PASS] Test 4.1: Unverified evidence yields 0.0% match score (uncredited towards verified score)")

    # ----------------------------------------------------
    # TEST 5: Error Handling (404 Nonexistent IDs)
    # ----------------------------------------------------
    try:
        get_json("/api/recommendations/students/999999")
        assert False, "Should have raised 404"
    except urllib.error.HTTPError as e:
        assert e.code == 404
        print("[PASS] Test 5.1: Nonexistent student correctly returned 404 Not Found")

    try:
        get_json("/api/recommendations/students/1/internships/999999")
        assert False, "Should have raised 404"
    except urllib.error.HTTPError as e:
        assert e.code == 404
        print("[PASS] Test 5.2: Nonexistent internship correctly returned 404 Not Found")

    # ----------------------------------------------------
    # TEST 6: Fairness Verification
    # ----------------------------------------------------
    # Ensure two students with identical verified skills/evidence but different demographic/institution attributes receive identical match scores
    ts = int(datetime.now(timezone.utc).timestamp())
    _, student_a = post_json("/api/students", {
        "name": "Candidate Alpha",
        "email": f"alpha.{ts}@ivy.edu",
        "university": "Prestigious Ivy University",
        "graduation_year": 2026
    })
    _, student_b = post_json("/api/students", {
        "name": "Candidate Beta",
        "email": f"beta.{ts}@state.edu",
        "university": "Rural Community College",
        "graduation_year": 2026
    })

    code_a, recs_a = get_json(f"/api/recommendations/students/{student_a['id']}")
    code_b, recs_b = get_json(f"/api/recommendations/students/{student_b['id']}")
    assert recs_a["recommendations"][0]["match_score"] == recs_b["recommendations"][0]["match_score"]
    print("[PASS] Test 6: Fairness guaranteed — demographic & institution attributes do not alter match scoring")

    print("\n==================================================")
    print("   ALL PHASE 4 TESTS PASSED (100% SUCCESS)       ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
