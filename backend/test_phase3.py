import urllib.request
import json

def test_api():
    base = "http://127.0.0.1:8000"
    
    # 1. Health
    res = urllib.request.urlopen(f"{base}/api/health")
    assert res.getcode() == 200
    health = json.loads(res.read())
    print("[PASS] /api/health:", health)
    
    # 2. Docs
    res = urllib.request.urlopen(f"{base}/api/docs")
    assert res.getcode() == 200
    print("[PASS] /api/docs accessible")

    # 3. GET /api/students/1
    res = urllib.request.urlopen(f"{base}/api/students/1")
    assert res.getcode() == 200
    student = json.loads(res.read())
    print(f"[PASS] GET /api/students/1: {student['name']} ({student['email']}), skills: {len(student['skills'])}, evidence: {len(student['evidence'])}")

    # 4. GET /api/skills
    res = urllib.request.urlopen(f"{base}/api/skills")
    assert res.getcode() == 200
    skills = json.loads(res.read())
    print(f"[PASS] GET /api/skills: found {len(skills)} skills")

    # 5. GET /api/students/1/evidence
    res = urllib.request.urlopen(f"{base}/api/students/1/evidence")
    assert res.getcode() == 200
    ev = json.loads(res.read())
    print(f"[PASS] GET /api/students/1/evidence: found {len(ev)} items")

    # 6. GET /api/internships
    res = urllib.request.urlopen(f"{base}/api/internships")
    assert res.getcode() == 200
    internships = json.loads(res.read())
    print(f"[PASS] GET /api/internships: found {len(internships)} internships")

    # 7. POST /api/students
    req_data = json.dumps({
        "name": "Maya Lin",
        "email": "maya.lin@berkeley.edu",
        "university": "UC Berkeley",
        "graduation_year": 2027
    }).encode("utf-8")
    req = urllib.request.Request(f"{base}/api/students", data=req_data, headers={"Content-Type": "application/json"})
    try:
        res = urllib.request.urlopen(req)
        assert res.getcode() == 201
        new_student = json.loads(res.read())
        print(f"[PASS] POST /api/students: created ID {new_student['id']}")
        student_id = new_student['id']
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[INFO] Student already exists from previous test run.")
            student_id = 1
        else:
            raise

    # 8. POST /api/evidence
    ev_data = json.dumps({
        "student_id": student_id,
        "evidence_type": "project",
        "title": "Autonomous Rover Navigation",
        "description": "Built SLAM pipeline with ROS and Python",
        "issuer": "Berkeley Robotics Lab",
        "verification_status": "verified"
    }).encode("utf-8")
    req = urllib.request.Request(f"{base}/api/evidence", data=ev_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.getcode() == 201
    new_ev = json.loads(res.read())
    print(f"[PASS] POST /api/evidence: created evidence ID {new_ev['id']}")

    # 9. POST /api/skills
    skill_data = json.dumps({
        "name": "Rust Systems Programming",
        "category": "Programming Languages",
        "description": "Memory-safe systems language"
    }).encode("utf-8")
    req = urllib.request.Request(f"{base}/api/skills", data=skill_data, headers={"Content-Type": "application/json"})
    try:
        res = urllib.request.urlopen(req)
        assert res.getcode() == 201
        new_sk = json.loads(res.read())
        print(f"[PASS] POST /api/skills: created skill ID {new_sk['id']}")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("[INFO] Skill already created from previous test run.")
        else:
            raise

    # 10. POST /api/internships
    internship_data = json.dumps({
        "title": "Robotics Software Intern",
        "company": "Boston Dynamics Partner",
        "description": "Control systems and perception algorithms",
        "location": "Boston, MA",
        "required_skills": ["Python", "Machine Learning"],
        "preferred_skills": ["Rust Systems Programming"]
    }).encode("utf-8")
    req = urllib.request.Request(f"{base}/api/internships", data=internship_data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.getcode() == 201
    new_internship = json.loads(res.read())
    print(f"[PASS] POST /api/internships: created internship ID {new_internship['id']}")

    # 11. CORS headers check
    req = urllib.request.Request(f"{base}/api/health", headers={"Origin": "http://localhost:3000"})
    res = urllib.request.urlopen(req)
    assert res.headers.get("access-control-allow-origin") == "http://localhost:3000"
    print("[PASS] CORS header for localhost:3000 passed")

    req = urllib.request.Request(f"{base}/api/health", headers={"Origin": "http://localhost:5173"})
    res = urllib.request.urlopen(req)
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"
    print("[PASS] CORS header for localhost:5173 passed")

    print("\n--- ALL PHASE 3 TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    test_api()
