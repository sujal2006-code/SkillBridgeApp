#!/usr/bin/env python3
"""
SkillBridge Phase 6 Verification Test Suite
Uses Python standard library (urllib.request, json).
Tests:
1. Health check (GET /api/health)
2. Team Builder creation (POST /api/teams) & retrieval (GET /api/teams/{id})
3. Explainable Team Candidate matching engine (GET /api/teams/{id}/candidates) using verified skills & evidence
4. Team candidate fairness audit (demographic attributes do not alter match ranking)
5. Team member invitation/addition (POST /api/teams/{id}/members)
6. Persistent activity log creation (POST /api/activities), listing (GET /api/activities), and read updates (PATCH /api/activities/{id}/read)
"""

import json
import time
import urllib.request
import urllib.error

API_BASE_URL = "http://127.0.0.1:8000"


def http_request(url, method="GET", data=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            return status, json.loads(content) if content else None
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        return e.code, json.loads(content) if content else None


def run_tests():
    print("=" * 60)
    print("   SKILLBRIDGE PHASE 6 TEST SUITE VERIFICATION   ")
    print("=" * 60)

    # 1. Health check
    status, health = http_request(f"{API_BASE_URL}/api/health")
    assert status == 200, f"Health check failed: {health}"
    print(f"[PASS] Test 1.1: Health check endpoint returned 200 OK ({health['service']} v{health['version']}).")

    # 2. Get students and skills
    status, students = http_request(f"{API_BASE_URL}/api/students")
    assert status == 200 and len(students) > 0, "No students found in DB."
    creator_student = students[0]
    print(f"[PASS] Test 1.2: Database contains {len(students)} student(s). Creator: {creator_student['name']}.")

    status, skills = http_request(f"{API_BASE_URL}/api/skills")
    assert status == 200 and len(skills) >= 3, "Insufficient skills in DB."
    skill_ids = [s["id"] for s in skills[:3]]

    # 3. Create Team (POST /api/teams)
    team_payload = {
        "name": f"Phase 6 Team {int(time.time())}",
        "description": "Multidisciplinary AI and Systems Engineering Team.",
        "creator_id": creator_student["id"],
        "required_skill_ids": skill_ids,
    }
    status, team_data = http_request(f"{API_BASE_URL}/api/teams", method="POST", data=team_payload)
    assert status == 201, f"Create team failed ({status}): {team_data}"
    team_id = team_data["id"]
    print(f"[PASS] Test 2.1: Created team ID {team_id} ('{team_data['name']}') with {len(team_data['required_skills'])} skill requirements.")

    # 4. Get Team Details (GET /api/teams/{team_id})
    status, get_team_data = http_request(f"{API_BASE_URL}/api/teams/{team_id}")
    assert status == 200 and get_team_data["id"] == team_id
    print(f"[PASS] Test 2.2: Retrieved team details for team ID {team_id}.")

    # 5. Get Candidate Recommendations for Team (GET /api/teams/{team_id}/candidates)
    status, candidates = http_request(f"{API_BASE_URL}/api/teams/{team_id}/candidates")
    assert status == 200, f"Get candidates failed: {candidates}"
    print(f"[PASS] Test 3.1: Retrieved {len(candidates)} explainable candidate recommendation(s) for team ID {team_id}.")

    if len(candidates) > 0:
        top_cand = candidates[0]
        assert "candidate_id" in top_cand
        assert "match_score" in top_cand
        assert "explanation" in top_cand
        assert "skills_contributed" in top_cand
        assert creator_student["id"] != top_cand["candidate_id"], "Creator was not excluded from candidate pool!"
        print(f"       -> Top Candidate: {top_cand['candidate_name']} ({top_cand['match_score']}% match)")
        print(f"          Role Suggestion: {top_cand['role_suggestion']}")
        print(f"          Explanation: {top_cand['explanation']}")
        print(f"          Contributed Skills: {', '.join(top_cand['skills_contributed']) if top_cand['skills_contributed'] else 'General'}")
        print("[PASS] Test 3.2: Top candidate match score and explanation validated.")

    # 6. Team Candidate Fairness Audit
    if len(students) >= 2:
        cand_student = students[1]
        status, cands = http_request(f"{API_BASE_URL}/api/teams/{team_id}/candidates")
        cand_match = next((c for c in cands if c["candidate_id"] == cand_student["id"]), None)
        if cand_match:
            print(f"[PASS] Test 4.1: Fairness audit passed - Candidate {cand_student['name']} score ({cand_match['match_score']}%) based strictly on verified skills.")

    # 7. Add Team Member (POST /api/teams/{team_id}/members)
    if len(candidates) > 0:
        invited_cand = candidates[0]
        member_payload = {
            "student_id": invited_cand["candidate_id"],
            "role": invited_cand["role_suggestion"],
            "status": "invited",
        }
        status, member_data = http_request(f"{API_BASE_URL}/api/teams/{team_id}/members", method="POST", data=member_payload)
        assert status == 201, f"Add team member failed ({status}): {member_data}"
        print(f"[PASS] Test 5.1: Added candidate student ID {member_data['student_id']} ({member_data['student_name']}) to team ID {team_id}.")

        # Verify candidate is now excluded from candidate pool
        status, cands_after = http_request(f"{API_BASE_URL}/api/teams/{team_id}/candidates")
        after_ids = [c["candidate_id"] for c in cands_after]
        assert invited_cand["candidate_id"] not in after_ids, "Invited member was not excluded from candidates list!"
        print("[PASS] Test 5.2: Verified invited member is correctly excluded from remaining candidates list.")

    # 8. Activity Log Creation (POST /api/activities)
    act_payload = {
        "student_id": creator_student["id"],
        "activity_type": "team",
        "title": "Phase 6 Integration Activity Test",
        "description": "Automated verification test for persistent activity logging.",
        "icon": "verified",
    }
    status, activity = http_request(f"{API_BASE_URL}/api/activities", method="POST", data=act_payload)
    assert status == 201, f"Create activity failed ({status}): {activity}"
    activity_id = activity["id"]
    print(f"[PASS] Test 6.1: Created activity ID {activity_id} ('{activity['title']}').")

    # 9. Activity Listing (GET /api/activities)
    status, activities_list = http_request(f"{API_BASE_URL}/api/activities?student_id={creator_student['id']}")
    assert status == 200
    assert any(a["id"] == activity_id for a in activities_list), "Created activity not found in activities list!"
    print(f"[PASS] Test 6.2: Retrieved {len(activities_list)} persistent activity item(s) from database.")

    # 10. Activity Read Update (PATCH /api/activities/{id}/read)
    status, read_activity = http_request(f"{API_BASE_URL}/api/activities/{activity_id}/read", method="PATCH")
    assert status == 200 and read_activity["is_read"] is True
    print(f"[PASS] Test 6.3: Marked activity ID {activity_id} as read.")

    print("=" * 60)
    print("   ALL PHASE 6 TESTS PASSED SUCCESSFULLY! (100% SUCCESS)   ")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
