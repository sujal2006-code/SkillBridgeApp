from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.session import Base, engine
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.internship import Internship, InternshipSkill
from app.models.match import Match
from app.models.otp import OTP



from sqlalchemy import inspect, text
from app.core.security import hash_password


def init_db(db: Session) -> None:
    """Create all database tables and seed initial demo data if empty."""
    # 1. Create tables
    Base.metadata.create_all(bind=engine)

    # 1b. Ensure new student columns exist if table was previously created
    inspector = inspect(engine)
    if "students" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("students")]
        with engine.begin() as conn:
            if "password_hash" not in columns:
                conn.execute(text("ALTER TABLE students ADD COLUMN password_hash VARCHAR(255)"))
            if "last_screen" not in columns:
                conn.execute(text("ALTER TABLE students ADD COLUMN last_screen VARCHAR(50) DEFAULT 'dashboard'"))
            if "last_state_json" not in columns:
                conn.execute(text("ALTER TABLE students ADD COLUMN last_state_json VARCHAR(2000)"))

    # 2. Seed Skills if not already present
    if db.query(Skill).count() == 0:
        skills_data = [
            {"name": "Python", "category": "Programming Languages", "description": "High-level programming language for general purpose, AI, and web development."},
            {"name": "React", "category": "Frontend Development", "description": "Component-based UI library for web interfaces."},
            {"name": "FastAPI", "category": "Backend Development", "description": "Modern high-performance web framework for building APIs with Python."},
            {"name": "SQL & PostgreSQL", "category": "Databases", "description": "Relational database modeling, indexing, query optimization, and transaction management."},
            {"name": "Machine Learning", "category": "AI / Data Science", "description": "Applied ML, feature engineering, neural networks, and model evaluation."},
            {"name": "TypeScript", "category": "Programming Languages", "description": "Typed superset of JavaScript for robust application development."},
            {"name": "Cloud & Docker", "category": "DevOps / Infrastructure", "description": "Containerization, cloud deployments, and CI/CD pipelines."},
            {"name": "RESTful API Design", "category": "Backend Development", "description": "Design, documentation, and security for REST APIs."},
        ]

        skill_objs = {}
        for s in skills_data:
            skill = Skill(**s)
            db.add(skill)
            db.flush()
            skill_objs[s["name"]] = skill

        # 3. Seed Demo Student
        demo_student = Student(
            name="Alex Rivera",
            email="alex.rivera@stanford.edu",
            university="Stanford University",
            graduation_year=2026,
        )
        db.add(demo_student)
        db.flush()

        # 4. Seed Student Skills (Verified Passport Skills)
        student_skills = [
            {"skill_id": skill_objs["Python"].id, "proficiency_level": "Advanced", "verification_status": "verified", "verified_at": datetime.now(timezone.utc)},
            {"skill_id": skill_objs["FastAPI"].id, "proficiency_level": "Intermediate", "verification_status": "verified", "verified_at": datetime.now(timezone.utc)},
            {"skill_id": skill_objs["React"].id, "proficiency_level": "Intermediate", "verification_status": "verified", "verified_at": datetime.now(timezone.utc)},
            {"skill_id": skill_objs["Machine Learning"].id, "proficiency_level": "Intermediate", "verification_status": "verified", "verified_at": datetime.now(timezone.utc)},
            {"skill_id": skill_objs["SQL & PostgreSQL"].id, "proficiency_level": "Intermediate", "verification_status": "verified", "verified_at": datetime.now(timezone.utc)},
        ]
        for ss in student_skills:
            db.add(StudentSkill(student_id=demo_student.id, **ss))

        # 5. Seed Evidence Items (All supported evidence types)
        evidence_items = [
            {
                "student_id": demo_student.id,
                "skill_id": skill_objs["Machine Learning"].id,
                "evidence_type": "coursework",
                "title": "CS229 Machine Learning Coursework",
                "description": "Completed end-to-end coursework covering supervised learning, neural network architectures, and reinforcement learning.",
                "issuer": "Stanford University Computer Science Dept",
                "verification_status": "verified",
                "evidence_url": "https://stanford.edu/coursework/cs229-verification",
            },
            {
                "student_id": demo_student.id,
                "skill_id": skill_objs["FastAPI"].id,
                "evidence_type": "project",
                "title": "SkillBridge Verification Engine",
                "description": "Architected full-stack verification engine using FastAPI, Pydantic, and SQLite/PostgreSQL.",
                "issuer": "GitHub Project Verification",
                "verification_status": "verified",
                "evidence_url": "https://github.com/skillbridge/verification-engine",
            },
            {
                "student_id": demo_student.id,
                "skill_id": skill_objs["Python"].id,
                "evidence_type": "competition",
                "title": "HackMIT 2025 - 1st Place AI Track",
                "description": "Developed real-time multi-agent reasoning system evaluated against benchmark datasets.",
                "issuer": "HackMIT Committee",
                "verification_status": "verified",
                "evidence_url": "https://hackmit.org/winners/2025/ai-track",
            },
            {
                "student_id": demo_student.id,
                "skill_id": skill_objs["Cloud & Docker"].id,
                "evidence_type": "certificate",
                "title": "AWS Certified Cloud Practitioner",
                "description": "Validated foundational cloud architecture, security, and deployment competencies.",
                "issuer": "Amazon Web Services",
                "verification_status": "verified",
                "evidence_url": "https://aws.amazon.com/verification/AWS-CERT-94821",
            },
            {
                "student_id": demo_student.id,
                "skill_id": skill_objs["React"].id,
                "evidence_type": "internship",
                "title": "Frontend Engineering Intern (Summer 2025)",
                "description": "Built responsive dashboard interfaces and state synchronization pipeline.",
                "issuer": "Apex Data Labs",
                "verification_status": "verified",
                "evidence_url": "https://apexdata.io/internships/verify/alex-rivera",
            },
        ]
        for ev in evidence_items:
            db.add(Evidence(**ev))

        # 6. Seed Additional Peer Candidates (For Team Builder & Candidate Matching)
        peer_students = [
            {
                "name": "Sarah Chen",
                "email": "sarah.chen@berkeley.edu",
                "university": "UC Berkeley",
                "graduation_year": 2026,
                "skills": [
                    {"skill_name": "React", "proficiency_level": "Advanced"},
                    {"skill_name": "TypeScript", "proficiency_level": "Advanced"},
                    {"skill_name": "RESTful API Design", "proficiency_level": "Intermediate"},
                ],
                "evidence": [
                    {
                        "skill_name": "React",
                        "evidence_type": "project",
                        "title": "Design System & React Component UI",
                        "description": "Built accessible WCAG 2.1 AA compliant UI component architecture.",
                        "issuer": "Cal Hacks Project Showcase",
                    },
                    {
                        "skill_name": "TypeScript",
                        "evidence_type": "coursework",
                        "title": "CS61B Advanced Data Structures in TypeScript",
                        "description": "Strict type-safe systems and data structures verification.",
                        "issuer": "UC Berkeley EECS",
                    },
                ],
            },
            {
                "name": "Marcus Vance",
                "email": "marcus.vance@cmu.edu",
                "university": "Carnegie Mellon University",
                "graduation_year": 2026,
                "skills": [
                    {"skill_name": "Machine Learning", "proficiency_level": "Advanced"},
                    {"skill_name": "Python", "proficiency_level": "Advanced"},
                    {"skill_name": "SQL & PostgreSQL", "proficiency_level": "Intermediate"},
                ],
                "evidence": [
                    {
                        "skill_name": "Machine Learning",
                        "evidence_type": "competition",
                        "title": "Kaggle Grandmaster Track - Multi-Modal Reasoning",
                        "description": "Built ensemble vision transformer models with 94.2% validation score.",
                        "issuer": "Kaggle / CMU AI Club",
                    },
                ],
            },
            {
                "name": "Elena Rostova",
                "email": "elena.rostova@gatech.edu",
                "university": "Georgia Tech",
                "graduation_year": 2027,
                "skills": [
                    {"skill_name": "FastAPI", "proficiency_level": "Advanced"},
                    {"skill_name": "SQL & PostgreSQL", "proficiency_level": "Advanced"},
                    {"skill_name": "Python", "proficiency_level": "Advanced"},
                ],
                "evidence": [
                    {
                        "skill_name": "FastAPI",
                        "evidence_type": "project",
                        "title": "High-Throughput Microservice Gateway",
                        "description": "Engineered asynchronous FastAPI microservice handling 15k req/sec.",
                        "issuer": "Georgia Tech Distributed Systems Lab",
                    },
                ],
            },
            {
                "name": "Priyansh Sharma",
                "email": "priyansh.sharma@illinois.edu",
                "university": "UIUC",
                "graduation_year": 2026,
                "skills": [
                    {"skill_name": "Cloud & Docker", "proficiency_level": "Advanced"},
                    {"skill_name": "FastAPI", "proficiency_level": "Intermediate"},
                    {"skill_name": "React", "proficiency_level": "Intermediate"},
                ],
                "evidence": [
                    {
                        "skill_name": "Cloud & Docker",
                        "evidence_type": "certificate",
                        "title": "Docker Certified Associate & Kubernetes",
                        "description": "Multi-container orchestration and cloud-native architecture.",
                        "issuer": "Cloud Native Computing Foundation",
                    },
                ],
            },
        ]

        for peer_data in peer_students:
            peer = Student(
                name=peer_data["name"],
                email=peer_data["email"],
                university=peer_data["university"],
                graduation_year=peer_data["graduation_year"],
            )
            db.add(peer)
            db.flush()

            for sk in peer_data["skills"]:
                if sk["skill_name"] in skill_objs:
                    db.add(
                        StudentSkill(
                            student_id=peer.id,
                            skill_id=skill_objs[sk["skill_name"]].id,
                            proficiency_level=sk["proficiency_level"],
                            verification_status="verified",
                            verified_at=datetime.now(timezone.utc),
                        )
                    )

            for ev in peer_data["evidence"]:
                if ev["skill_name"] in skill_objs:
                    db.add(
                        Evidence(
                            student_id=peer.id,
                            skill_id=skill_objs[ev["skill_name"]].id,
                            evidence_type=ev["evidence_type"],
                            title=ev["title"],
                            description=ev["description"],
                            issuer=ev["issuer"],
                            verification_status="verified",
                        )
                    )

        # 7. Seed Demo Internships
        internship1 = Internship(
            title="Applied AI & Backend Engineering Intern",
            company="NeuroTech Innovations",
            description="Join our core platform engineering team to build scalable ML inference pipelines, REST APIs, and microservices.",
            location="Remote / San Francisco, CA",
            required_skills=["Python", "FastAPI", "SQL & PostgreSQL"],
            preferred_skills=["Machine Learning", "Cloud & Docker"],
        )
        db.add(internship1)
        db.flush()

        # Link required/preferred skills for Internship 1
        db.add(InternshipSkill(internship_id=internship1.id, skill_id=skill_objs["Python"].id, required=True, minimum_proficiency="Intermediate"))
        db.add(InternshipSkill(internship_id=internship1.id, skill_id=skill_objs["FastAPI"].id, required=True, minimum_proficiency="Intermediate"))
        db.add(InternshipSkill(internship_id=internship1.id, skill_id=skill_objs["SQL & PostgreSQL"].id, required=True, minimum_proficiency="Intermediate"))
        db.add(InternshipSkill(internship_id=internship1.id, skill_id=skill_objs["Machine Learning"].id, required=False, minimum_proficiency="Beginner"))
        db.add(InternshipSkill(internship_id=internship1.id, skill_id=skill_objs["Cloud & Docker"].id, required=False, minimum_proficiency="Beginner"))

        internship2 = Internship(
            title="Full-Stack Web Engineering Intern",
            company="CloudSphere Dynamics",
            description="Help develop student-facing portal features, reactive UI components, and resilient backend endpoints.",
            location="New York, NY (Hybrid)",
            required_skills=["React", "TypeScript", "Python"],
            preferred_skills=["FastAPI", "SQL & PostgreSQL"],
        )
        db.add(internship2)
        db.flush()

        # Link required/preferred skills for Internship 2
        db.add(InternshipSkill(internship_id=internship2.id, skill_id=skill_objs["React"].id, required=True, minimum_proficiency="Intermediate"))
        db.add(InternshipSkill(internship_id=internship2.id, skill_id=skill_objs["TypeScript"].id, required=True, minimum_proficiency="Intermediate"))
        db.add(InternshipSkill(internship_id=internship2.id, skill_id=skill_objs["Python"].id, required=True, minimum_proficiency="Beginner"))
        db.add(InternshipSkill(internship_id=internship2.id, skill_id=skill_objs["FastAPI"].id, required=False, minimum_proficiency="Beginner"))

        db.commit()
