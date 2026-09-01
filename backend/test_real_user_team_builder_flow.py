import time
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.team import Team, TeamMember
from app.models.skill import Skill
from app.models.evidence import Evidence
from app.core.security import create_access_token

client = TestClient(app)

def run_real_user_flow_test():
    print("=" * 80)
    print("VERIFY REAL USER -> SKILL PASSPORT -> TEAM BUILDER DISCOVERY FLOW")
    print("=" * 80)

    db = SessionLocal()

    # Step 0: Ensure Account A (Team Leader) exists
    aarav = db.query(Student).filter(Student.email == "aarav.sharma@skillbridge.edu").first()
    assert aarav is not None, "Leader Aarav must exist"
    token_aarav = create_access_token(aarav.id)
    headers_aarav = {"Authorization": f"Bearer {token_aarav}"}

    # Find Aarav's team
    team = db.query(Team).filter(Team.creator_id == aarav.id).first()
    if not team:
        team = Team(
            name="Hex Bridge AI Platform",
            project_name="AI & Full Stack Platform",
            description="Multidisciplinary engineering team",
            creator_id=aarav.id,
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        db.add(TeamMember(team_id=team.id, student_id=aarav.id, role="Team Leader", status="joined"))
        db.commit()

    team_id = team.id
    print(f"[OK] Account A (Leader): {aarav.name} (#{aarav.id}), Team #{team_id} ('{team.name}')")

    # Step 1: Account B creates their own SkillBridge account
    timestamp = int(time.time() * 1000)
    friend_name = f"Kavya Verma {timestamp % 10000}"
    friend_email = f"kavya.{timestamp}@skillbridge.edu"
    friend_pwd = "StrongPass2026!"

    print(f"\n--- STEP 1: Account B Registers ({friend_name} <{friend_email}>) ---")
    reg_payload = {
        "name": friend_name,
        "email": friend_email,
        "password": friend_pwd,
        "confirm_password": friend_pwd,
        "mode": "register",
        "university": "IIT Delhi",
        "graduation_year": 2026,
    }
    reg_resp = client.post("/api/students/login", json=reg_payload)
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    friend_data = reg_resp.json()
    friend_id = friend_data["student"]["id"]
    friend_token = friend_data["token"]
    headers_friend = {"Authorization": f"Bearer {friend_token}"}
    print(f" [PASS] Account B registered persistently with ID #{friend_id} at IIT Delhi")

    # Step 2: Complete profile & select professional role -> Backend Developer
    print(f"\n--- STEP 2: Account B Selects Professional Role (Backend Developer) ---")
    role_payload = {
        "primary_role": "Backend Developer",
        "secondary_specializations": ["Cloud & DevOps"],
        "bio": "Passionate backend engineer building distributed microservices.",
    }
    role_resp = client.put("/api/students/me/professional-role", json=role_payload, headers=headers_friend)
    assert role_resp.status_code == 200, f"Failed to set professional role: {role_resp.text}"
    role_data = role_resp.json()
    assert role_data["primary_role"] == "Backend Developer"
    print(f" [PASS] Account B professional identity saved: {role_data['primary_role']}")

    # Step 3: Account B has 0 verified skills initially -> check Team Builder candidate pool
    # A student with 0 verified skills should NOT appear in Team Builder (only verified candidates)
    tb_pre = client.get(f"/api/teams/{team_id}/candidates?target_role=Backend Developer")
    assert tb_pre.status_code == 200
    pre_candidates = tb_pre.json()
    assert not any(c["candidate_id"] == friend_id for c in pre_candidates), "Unverified candidate must not appear yet"
    print(f" [PASS] Confirmed: Account B with 0 verified skills does NOT appear yet in Team Builder")

    # Step 4: Account B adds coursework, projects, and certificates with skills
    print(f"\n--- STEP 3 & 4: Account B Adds Coursework, Projects & Certificates ---")
    ev1_payload = {
        "title": "High-Throughput E-Commerce Microservices",
        "description": "Architected Python FastAPI microservices with RESTful APIs handling 10k req/min.",
        "evidence_type": "project",
        "artifact_url": "https://github.com/kavya/ecommerce-microservices",
        "skill_names": ["Python", "FastAPI", "RESTful API Design"],
    }
    ev1_resp = client.post("/api/evidence", json=ev1_payload, headers=headers_friend)
    assert ev1_resp.status_code == 201, f"Failed to create evidence 1: {ev1_resp.text}"
    ev1_id = ev1_resp.json()["id"]

    ev2_payload = {
        "title": "PostgreSQL Relational Schema & Indexing",
        "description": "Designed partitioned SQL tables with transaction rollbacks and ACID compliance.",
        "evidence_type": "coursework",
        "artifact_url": "https://github.com/kavya/sql-database-engine",
        "skill_names": ["SQL & PostgreSQL"],
    }
    ev2_resp = client.post("/api/evidence", json=ev2_payload, headers=headers_friend)
    assert ev2_resp.status_code == 201
    ev2_id = ev2_resp.json()["id"]

    ev3_payload = {
        "title": "Open Source Git Workflow & CI Pipeline",
        "description": "Maintained multi-branch git repository with continuous integration checks.",
        "evidence_type": "competition",
        "artifact_url": "https://github.com/kavya/git-ci-pipeline",
        "skill_names": ["Git"],
    }
    ev3_resp = client.post("/api/evidence", json=ev3_payload, headers=headers_friend)
    assert ev3_resp.status_code == 201
    ev3_id = ev3_resp.json()["id"]

    # Add a complementary skill: Docker
    ev4_payload = {
        "title": "Docker Certified Associate Credential",
        "description": "Certified in multi-stage Docker containerization and daemon security.",
        "evidence_type": "certificate",
        "artifact_url": "https://credentials.docker.com/kavya-cert",
        "skill_names": ["Docker"],
    }
    ev4_resp = client.post("/api/evidence", json=ev4_payload, headers=headers_friend)
    assert ev4_resp.status_code == 201
    ev4_id = ev4_resp.json()["id"]

    print(f" [PASS] Account B submitted 4 evidence artifacts: #{ev1_id}, #{ev2_id}, #{ev3_id}, #{ev4_id}")

    # Step 5: Evidence verification (Admin reviews and approves)
    print(f"\n--- STEP 5: Admin Verifies All 4 Evidence Submissions ---")
    for ev_id in [ev1_id, ev2_id, ev3_id, ev4_id]:
        appr_resp = client.post(f"/api/admin/evidence/{ev_id}/approve")
        assert appr_resp.status_code == 200, f"Approval failed for evidence #{ev_id}: {appr_resp.text}"
    print(f" [PASS] All 4 evidence artifacts approved and verified in database")

    # Step 6: Verify Account B's Skill Passport contains all verified skills
    print(f"\n--- STEP 6: Verify Account B's Skill Passport ---")
    passport_resp = client.get(f"/api/students/{friend_id}", headers=headers_friend)
    assert passport_resp.status_code == 200
    passport_data = passport_resp.json()
    verified_skill_names = [s["skill"]["name"] for s in passport_data["skills"] if s["verification_status"] == "verified"]
    print(f" [PASS] Account B Skill Passport has verified skills: {verified_skill_names}")
    assert any("Python" in s for s in verified_skill_names)
    assert any("FastAPI" in s for s in verified_skill_names)
    assert any("REST" in s for s in verified_skill_names)
    assert any("SQL" in s for s in verified_skill_names)
    assert any("Git" in s for s in verified_skill_names)
    assert any("Docker" in s for s in verified_skill_names)

    # Step 7 & 8: Account A opens Team Builder and searches for "Backend Developer"
    print(f"\n--- STEP 7 & 8: Account A Opens Team Builder & Searches 'Backend Developer' ---")
    tb_resp = client.get(f"/api/teams/{team_id}/candidates?target_role=Backend Developer")
    assert tb_resp.status_code == 200
    tb_candidates = tb_resp.json()

    # Step 9: Account B MUST appear as a candidate!
    friend_rec = next((c for c in tb_candidates if c["candidate_id"] == friend_id), None)
    assert friend_rec is not None, f"Account B (#{friend_id}) MUST appear in Team Builder candidate recommendations!"
    print(f" [PASS] Account B (#{friend_id}) appears in Team Builder candidate recommendations!")

    # Step 10 & 11: Validate Account B's candidate card data
    print(f"\n--- STEP 9, 10 & 11: Detailed Candidate Card Verification for Account B ---")
    print(f" Candidate Name:        {friend_rec['candidate_name']} (Expected: {friend_name})")
    print(f" Professional Role:     {friend_rec['professional_role']} (Expected: Backend Developer)")
    print(f" University:            {friend_rec['university']} (Expected: IIT Delhi)")
    print(f" Match Score:           {friend_rec['match_score']}% (Expected: 100.0%)")
    print(f" Core Skills Fulfilled: {friend_rec['core_skills_fulfilled']}")
    print(f" Core Skills Missing:   {friend_rec['core_skills_missing']}")
    print(f" Complementary Skills:  {friend_rec['complementary_skills']}")
    print(f" Explanation:           {friend_rec['explanation']}")
    print(f" Evidence Breakdown:    {len(friend_rec['evidence_breakdown'])} artifacts")

    assert friend_rec["candidate_name"] == friend_name
    assert friend_rec["professional_role"] == "Backend Developer"
    assert friend_rec["university"] == "IIT Delhi"
    assert friend_rec["match_score"] == 100.0, f"Expected 100% Backend match, got {friend_rec['match_score']}%"
    assert len(friend_rec["core_skills_fulfilled"]) == 5
    assert len(friend_rec["core_skills_missing"]) == 0
    assert any("Docker" in s for s in friend_rec["complementary_skills"])
    assert not any("Docker" in s for s in friend_rec["core_skills_fulfilled"])  # Docker is complementary, not core
    assert len(friend_rec["evidence_breakdown"]) >= 3

    # Step 12: Check that Account A (Leader) is NEVER in candidate list
    assert not any(c["candidate_id"] == aarav.id for c in tb_candidates), "Logged in user must be excluded"
    print(f" [PASS] Confirmed: Account A (Leader) is excluded from candidate recommendations")

    # Step 13: Check cross-domain isolation for Account B
    # When searching for Frontend Developer, Account B (who only has Git from Frontend) should get 20.0%!
    tb_front = client.get(f"/api/teams/{team_id}/candidates?target_role=Frontend Developer")
    friend_front = next((c for c in tb_front.json() if c["candidate_id"] == friend_id), None)
    assert friend_front is not None
    assert friend_front["match_score"] == 20.0, f"Expected 20% Frontend match (Git only), got {friend_front['match_score']}%"
    print(f" [PASS] Cross-domain isolation: Account B scored exactly 20.0% for Frontend (Git fulfilled, HTML/CSS/JS/React missing)")

    print("\n" + "=" * 80)
    print("REAL USER -> SKILL PASSPORT -> TEAM BUILDER VERIFIED WITH 100% ACCURACY!")
    print("=" * 80)

if __name__ == "__main__":
    run_real_user_flow_test()
