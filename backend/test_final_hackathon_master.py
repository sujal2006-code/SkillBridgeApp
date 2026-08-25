import os
import sys
import time
import functools

print = functools.partial(print, flush=True)

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.team import Team, TeamMember, TeamSkillRequirement

client = TestClient(app)

def run_final_hackathon_verification():
    print("================================================================================")
    print("SKILLBRIDGE FINAL MASTER HACKATHON VERIFICATION SUITE")
    print("================================================================================")
    
    db = SessionLocal()
    try:
        # Helper to get or create skill
        def get_or_create_skill(name: str) -> Skill:
            sk = db.query(Skill).filter(Skill.name.ilike(name.strip())).first()
            if not sk:
                sk = Skill(name=name.strip(), category="Technical", description=f"Skill in {name}")
                db.add(sk)
                db.flush()
            return sk

        ts = int(time.time() * 1000)
        
        # ----------------------------------------------------------------------------
        # 1. FRONTEND TEAM MATCHING TEST (Ananya Verma vs Rohan Mehta)
        # ----------------------------------------------------------------------------
        print("\n--- [TEST 1] Frontend Team Matching Evaluation ---")
        creator = db.query(Student).first()
        assert creator is not None

        fe_team = Team(name=f"Modern Web UX Team {ts}", description="NextGen React Web App", creator_id=creator.id)
        db.add(fe_team)
        db.flush()

        for s_name in ["React", "JavaScript", "HTML", "CSS"]:
            sk_obj = get_or_create_skill(s_name)
            db.add(TeamSkillRequirement(team_id=fe_team.id, skill_id=sk_obj.id, minimum_proficiency="Intermediate", required=True))
        db.commit()

        fe_cands = client.get(f"/api/teams/{fe_team.id}/candidates").json()
        
        ananya_rec = next((c for c in fe_cands if c["candidate_name"] == "Ananya Verma"), None)
        assert ananya_rec is not None, "Ananya Verma not found in candidate list!"
        assert ananya_rec["match_score"] >= 80.0, f"Expected Ananya >= 80%, got {ananya_rec['match_score']}%"
        assert len(ananya_rec["skills_contributed"]) >= 4
        assert len(ananya_rec["missing_team_skills"]) == 0
        assert "React" in ananya_rec["explanation"]
        print(f" [PASS] Frontend Candidate Ananya Verma: Score: {ananya_rec['match_score']}%, Matched: {ananya_rec['skills_contributed']}, Missing: {ananya_rec['missing_team_skills']}")
        print(f"        Explanation: \"{ananya_rec['explanation']}\"")

        rohan_rec = next((c for c in fe_cands if c["candidate_name"] == "Rohan Mehta"), None)
        if rohan_rec:
            assert rohan_rec["match_score"] < 35.0, f"Expected Rohan Mehta < 35% on Frontend team, got {rohan_rec['match_score']}%"
            assert len(rohan_rec["missing_team_skills"]) >= 3
            print(f" [PASS] Backend Candidate Rohan Mehta on Frontend Team: Score: {rohan_rec['match_score']}%, Missing: {rohan_rec['missing_team_skills']}")

        # ----------------------------------------------------------------------------
        # 2. BACKEND TEAM MATCHING TEST (Rohan Mehta vs Ananya Verma)
        # ----------------------------------------------------------------------------
        print("\n--- [TEST 2] Backend Team Matching Evaluation ---")
        be_team = Team(name=f"High-Load Microservices Team {ts}", description="FastAPI and SQL backend engine", creator_id=creator.id)
        db.add(be_team)
        db.flush()

        for s_name in ["SQL", "FastAPI", "Python"]:
            sk_obj = get_or_create_skill(s_name)
            db.add(TeamSkillRequirement(team_id=be_team.id, skill_id=sk_obj.id, minimum_proficiency="Intermediate", required=True))
        db.commit()

        be_cands = client.get(f"/api/teams/{be_team.id}/candidates").json()

        rohan_be_rec = next((c for c in be_cands if c["candidate_name"] == "Rohan Mehta"), None)
        assert rohan_be_rec is not None, "Rohan Mehta not found in candidate list!"
        assert rohan_be_rec["match_score"] >= 80.0, f"Expected Rohan >= 80%, got {rohan_be_rec['match_score']}%"
        assert len(rohan_be_rec["missing_team_skills"]) == 0
        assert "FastAPI" in rohan_be_rec["skills_contributed"]
        assert "SQL" in rohan_be_rec["skills_contributed"] or "PostgreSQL" in rohan_be_rec["skills_contributed"]
        print(f" [PASS] Backend Candidate Rohan Mehta: Score: {rohan_be_rec['match_score']}%, Matched: {rohan_be_rec['skills_contributed']}, Missing: {rohan_be_rec['missing_team_skills']}")
        print(f"        Explanation: \"{rohan_be_rec['explanation']}\"")

        ananya_be_rec = next((c for c in be_cands if c["candidate_name"] == "Ananya Verma"), None)
        if ananya_be_rec:
            assert ananya_be_rec["match_score"] < 35.0, f"Expected Ananya < 35% on Backend team, got {ananya_be_rec['match_score']}%"
            print(f" [PASS] Frontend Candidate Ananya Verma on Backend Team: Score: {ananya_be_rec['match_score']}%, Missing: {ananya_be_rec['missing_team_skills']}")

        # ----------------------------------------------------------------------------
        # 3. DATA SCIENCE & AI/ML TEAM MATCHING TEST
        # ----------------------------------------------------------------------------
        print("\n--- [TEST 3] Data Science & AI/ML Team Matching Evaluation ---")
        ds_team = Team(name=f"Predictive ML Analytics Team {ts}", description="Python, Pandas and ML models", creator_id=creator.id)
        db.add(ds_team)
        db.flush()

        for s_name in ["Python", "Pandas", "Machine Learning", "Data Science"]:
            sk_obj = get_or_create_skill(s_name)
            db.add(TeamSkillRequirement(team_id=ds_team.id, skill_id=sk_obj.id, minimum_proficiency="Intermediate", required=True))
        db.commit()

        ds_cands = client.get(f"/api/teams/{ds_team.id}/candidates").json()

        aditya_ds_rec = next((c for c in ds_cands if c["candidate_name"] == "Aditya Nair"), None)
        assert aditya_ds_rec is not None, "Aditya Nair not found!"
        assert aditya_ds_rec["match_score"] >= 80.0, f"Expected Aditya Nair >= 80%, got {aditya_ds_rec['match_score']}%"
        print(f" [PASS] Data Scientist Aditya Nair: Score: {aditya_ds_rec['match_score']}%, Matched: {aditya_ds_rec['skills_contributed']}")

        priya_ai_rec = next((c for c in ds_cands if c["candidate_name"] == "Priya Iyer"), None)
        assert priya_ai_rec is not None, "Priya Iyer not found!"
        assert priya_ai_rec["match_score"] >= 80.0, f"Expected Priya Iyer >= 80%, got {priya_ai_rec['match_score']}%"
        print(f" [PASS] AI/ML Engineer Priya Iyer: Score: {priya_ai_rec['match_score']}%, Matched: {priya_ai_rec['skills_contributed']}")

        # ----------------------------------------------------------------------------
        # 4. ACCURATE MISSING SKILLS CALCULATION TEST
        # ----------------------------------------------------------------------------
        print("\n--- [TEST 4] Accurate Missing Skills Calculation ---")
        mixed_team = Team(name=f"FullStack Cloud Team {ts}", description="React, SQL, FastAPI, Docker", creator_id=creator.id)
        db.add(mixed_team)
        db.flush()

        for s_name in ["SQL", "FastAPI", "React", "Docker"]:
            sk_obj = get_or_create_skill(s_name)
            db.add(TeamSkillRequirement(team_id=mixed_team.id, skill_id=sk_obj.id, minimum_proficiency="Intermediate", required=True))
        db.commit()

        mixed_cands = client.get(f"/api/teams/{mixed_team.id}/candidates").json()
        rohan_mixed = next((c for c in mixed_cands if c["candidate_name"] == "Rohan Mehta"), None)
        assert rohan_mixed is not None
        # Rohan has SQL, FastAPI, Docker, Python, but lacks React!
        assert "React" in rohan_mixed["missing_team_skills"], f"Expected 'React' in missing skills, got: {rohan_mixed['missing_team_skills']}"
        assert "FastAPI" not in rohan_mixed["missing_team_skills"]
        print(f" [PASS] Rohan Mehta accurately shows missing skills: {rohan_mixed['missing_team_skills']} (Matched: {rohan_mixed['skills_contributed']})")

        # ----------------------------------------------------------------------------
        # 5. DYNAMIC EVIDENCE VERIFICATION CYCLE TEST
        # ----------------------------------------------------------------------------
        print("\n--- [TEST 5] Dynamic Evidence Verification Lifecycle ---")
        # Step A: Register new test candidate
        candidate_name = f"LifecycleCandidate_{ts}"
        reg_res = client.post("/api/students/login", json={
            "name": candidate_name,
            "password": "Password123",
            "confirm_password": "Password123",
            "mode": "register"
        })
        assert reg_res.status_code == 200
        cand_id = reg_res.json()["student"]["id"]
        cand_token = reg_res.json()["token"]

        # Step B: Submit & verify initial skill (Python)
        ev1 = client.post("/api/evidence", json={
            "title": "Python Core System",
            "description": "Scripting and algorithms in Python",
            "evidence_type": "project",
            "skill_names": ["Python"],
        }, headers={"Authorization": f"Bearer {cand_token}"}).json()
        
        client.post(f"/api/admin/evidence/{ev1['id']}/approve", headers={"Authorization": "Bearer admin-session-token-sujal-verified"})

        # Check candidate match for backend team (requires SQL, FastAPI, Python)
        recs_v1 = client.get(f"/api/teams/{be_team.id}/candidates").json()
        cand_rec_v1 = next((c for c in recs_v1 if c["candidate_id"] == cand_id), None)
        assert cand_rec_v1 is not None
        score_v1 = cand_rec_v1["match_score"]
        assert "Python" in cand_rec_v1["skills_contributed"]
        assert "FastAPI" in cand_rec_v1["missing_team_skills"]
        print(f" [PASS] Cycle Step 1: Candidate with Python has Match Score: {score_v1}%, Missing: {cand_rec_v1['missing_team_skills']}")

        # Step C: Submit & verify second skill (SQL)
        ev2 = client.post("/api/evidence", json={
            "title": "SQL Relational DB Modeling",
            "description": "PostgreSQL queries and schema design",
            "evidence_type": "project",
            "skill_names": ["SQL"],
        }, headers={"Authorization": f"Bearer {cand_token}"}).json()
        
        client.post(f"/api/admin/evidence/{ev2['id']}/approve", headers={"Authorization": "Bearer admin-session-token-sujal-verified"})

        recs_v2 = client.get(f"/api/teams/{be_team.id}/candidates").json()
        cand_rec_v2 = next((c for c in recs_v2 if c["candidate_id"] == cand_id), None)
        assert cand_rec_v2 is not None
        score_v2 = cand_rec_v2["match_score"]
        assert score_v2 > score_v1, f"Expected score_v2 ({score_v2}) > score_v1 ({score_v1})"
        assert "FastAPI" in cand_rec_v2["missing_team_skills"]
        print(f" [PASS] Cycle Step 2: Added SQL evidence -> Match Score INCREASED to {score_v2}%, Missing: {cand_rec_v2['missing_team_skills']}")

        # Step D: Submit & verify third skill (FastAPI)
        ev3 = client.post("/api/evidence", json={
            "title": "FastAPI Web Microservice",
            "description": "Async REST endpoints with Pydantic",
            "evidence_type": "project",
            "skill_names": ["FastAPI"],
        }, headers={"Authorization": f"Bearer {cand_token}"}).json()
        
        client.post(f"/api/admin/evidence/{ev3['id']}/approve", headers={"Authorization": "Bearer admin-session-token-sujal-verified"})

        recs_v3 = client.get(f"/api/teams/{be_team.id}/candidates").json()
        cand_rec_v3 = next((c for c in recs_v3 if c["candidate_id"] == cand_id), None)
        assert cand_rec_v3 is not None
        score_v3 = cand_rec_v3["match_score"]
        assert score_v3 > score_v2, f"Expected score_v3 ({score_v3}) > score_v2 ({score_v2})"
        assert len(cand_rec_v3["missing_team_skills"]) == 0
        print(f" [PASS] Cycle Step 3: Added FastAPI evidence -> Match Score INCREASED to {score_v3}%, Missing: None (100% Gaps Satisfied!)")

        # ----------------------------------------------------------------------------
        # 6. DETERMINISTIC STABILITY CHECK
        # ----------------------------------------------------------------------------
        print("\n--- [TEST 6] Deterministic Stability Test ---")
        scores = []
        for _ in range(5):
            res = client.get(f"/api/teams/{be_team.id}/candidates").json()
            r_rec = next(c for c in res if c["candidate_name"] == "Rohan Mehta")
            scores.append(r_rec["match_score"])
        assert len(set(scores)) == 1, f"Scores are not deterministic: {scores}"
        print(f" [PASS] 5 consecutive calculations produced identical deterministic score: {scores[0]}%")

        print("\n================================================================================")
        print("ALL FINAL HACKATHON SUITE TESTS COMPLETED WITH 100% SUCCESS!")
        print("================================================================================")

    finally:
        db.close()

if __name__ == "__main__":
    run_final_hackathon_verification()
