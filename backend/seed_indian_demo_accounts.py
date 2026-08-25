import os
import sys
import functools

print = functools.partial(print, flush=True)

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.core.security import hash_password

REQUIRED_DEMO_ACCOUNTS = [
    {
        "name": "Ananya Verma",
        "email": "ananya.verma@skillbridge.edu",
        "university": "IIT Delhi (Design & Computing)",
        "graduation_year": 2026,
        "skills": [
            {"name": "HTML", "level": "Advanced"},
            {"name": "CSS", "level": "Advanced"},
            {"name": "JavaScript", "level": "Advanced"},
            {"name": "React", "level": "Advanced"},
            {"name": "TypeScript", "level": "Advanced"},
            {"name": "UI/UX", "level": "Advanced"},
            {"name": "Tailwind CSS", "level": "Advanced"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Design System & React Component Library for Accessible EdTech",
                "description": "Engineered WCAG AAA accessible design system with React, TypeScript, Tailwind CSS, and Storybook components.",
                "issuer": "IIT Delhi Design Innovation Center",
                "url": "https://github.com/ananya-verma/edtech-ui-system",
                "skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "UI/UX", "Tailwind CSS"],
            },
            {
                "type": "certificate",
                "title": "Advanced Frontend Architecture & Web Performance",
                "description": "Certified in Core Web Vitals optimization, React concurrent rendering, and TypeScript state patterns.",
                "issuer": "Frontend Masters / Meta",
                "url": "https://frontendmasters.com/verify/ananya-verma-2025",
                "skills": ["React", "TypeScript", "JavaScript"],
            }
        ]
    },
    {
        "name": "Rohan Mehta",
        "email": "rohan.mehta@skillbridge.edu",
        "university": "BITS Pilani (Computer Science)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Python", "level": "Advanced"},
            {"name": "FastAPI", "level": "Advanced"},
            {"name": "SQL", "level": "Advanced"},
            {"name": "PostgreSQL", "level": "Advanced"},
            {"name": "REST API", "level": "Advanced"},
            {"name": "Git", "level": "Intermediate"},
            {"name": "Docker", "level": "Intermediate"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "High-Throughput Distributed Payment Gateway Engine",
                "description": "Constructed asynchronous microservices with FastAPI and PostgreSQL connection pooling handling 8,000 requests/second.",
                "issuer": "BITS Pilani Center for Software Engineering",
                "url": "https://github.com/rohan-mehta/fastapi-paycore",
                "skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "REST API", "Git"],
            },
            {
                "type": "certificate",
                "title": "PostgreSQL High Performance Query Tuning & Architecture",
                "description": "Advanced database optimization, B-Tree index tuning, and replication clustering.",
                "issuer": "PostgreSQL Experts Inc.",
                "url": "https://pganalyze.com/verify/rohan-mehta-pg2025",
                "skills": ["SQL", "PostgreSQL", "Python"],
            }
        ]
    },
    {
        "name": "Aditya Nair",
        "email": "aditya.nair@skillbridge.edu",
        "university": "IIT Madras (Data Science & Analytics)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Python", "level": "Advanced"},
            {"name": "SQL", "level": "Advanced"},
            {"name": "Pandas", "level": "Advanced"},
            {"name": "NumPy", "level": "Advanced"},
            {"name": "Data Science", "level": "Advanced"},
            {"name": "Machine Learning", "level": "Advanced"},
            {"name": "Data Visualization", "level": "Intermediate"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Predictive Macroeconomic Forecasting Engine for Indian Supply Chains",
                "description": "Constructed time-series econometric models with Python, Pandas, NumPy, and SQL pipelines for agricultural logistics forecasting.",
                "issuer": "IIT Madras Data Science Lab",
                "url": "https://github.com/aditya-nair/supply-chain-analytics",
                "skills": ["Python", "SQL", "Pandas", "NumPy", "Data Science", "Machine Learning", "Data Visualization"],
            },
            {
                "type": "competition",
                "title": "Top 1% Kaggle Grandmaster Challenge - Financial Risk Modeling",
                "description": "Developed ensemble gradient boosted regressors and exploratory data analysis notebooks.",
                "issuer": "Kaggle / Google Cloud",
                "url": "https://kaggle.com/certificates/aditya-nair-2025",
                "skills": ["Data Science", "Python", "Pandas", "Machine Learning"],
            }
        ]
    },
    {
        "name": "Priya Iyer",
        "email": "priya.iyer@skillbridge.edu",
        "university": "IISc Bangalore (Artificial Intelligence)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Python", "level": "Advanced"},
            {"name": "Machine Learning", "level": "Advanced"},
            {"name": "Data Science", "level": "Advanced"},
            {"name": "NumPy", "level": "Advanced"},
            {"name": "Pandas", "level": "Advanced"},
            {"name": "NLP", "level": "Advanced"},
            {"name": "Deep Learning", "level": "Intermediate"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Cross-Lingual Biomedical Information Extraction using Domain-Adapted Transformers",
                "description": "Fine-tuned multilingual BERT models with PyTorch and NLP tokenizers across 12 Indian regional medical datasets.",
                "issuer": "IISc Bangalore Computational Linguistics Center",
                "url": "https://github.com/priya-iyer/indic-biomed-nlp",
                "skills": ["Python", "Machine Learning", "NLP", "Data Science", "Pandas", "NumPy"],
            },
            {
                "type": "certificate",
                "title": "Stanford Online: Natural Language Processing with Deep Learning",
                "description": "CS224N specialization on attention mechanisms, transformer architectures, and generative language modeling.",
                "issuer": "Stanford University / Coursera",
                "url": "https://coursera.org/verify/STANFORD-PRIYA-NLP",
                "skills": ["NLP", "Machine Learning", "Python"],
            }
        ]
    },
    {
        "name": "Arjun Kapoor",
        "email": "arjun.kapoor@skillbridge.edu",
        "university": "IIT Roorkee (Computer Science)",
        "graduation_year": 2026,
        "skills": [
            {"name": "HTML", "level": "Advanced"},
            {"name": "CSS", "level": "Advanced"},
            {"name": "JavaScript", "level": "Advanced"},
            {"name": "React", "level": "Advanced"},
            {"name": "Python", "level": "Advanced"},
            {"name": "FastAPI", "level": "Advanced"},
            {"name": "SQL", "level": "Advanced"},
            {"name": "PostgreSQL", "level": "Intermediate"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Full-Stack Collaborative Workspace with Real-Time WebSockets & Database Sync",
                "description": "Engineered responsive React web client coupled to asynchronous FastAPI backend with PostgreSQL relational schema and Redis caching.",
                "issuer": "IIT Roorkee Annual Hackathon",
                "url": "https://github.com/arjun-kapoor/workspace-fullstack",
                "skills": ["HTML", "CSS", "JavaScript", "React", "Python", "FastAPI", "SQL", "PostgreSQL"],
            },
            {
                "type": "competition",
                "title": "Winner - National Full Stack Hackathon 2025",
                "description": "Architected end-to-end cloud platform combining modern React interfaces and scalable FastAPI microservices.",
                "issuer": "Ministry of Electronics & IT (MeitY)",
                "url": "https://innovateindia.mygov.in/certificates/arjun-kapoor-2025",
                "skills": ["React", "FastAPI", "Python", "JavaScript", "SQL"],
            }
        ]
    }
]

def seed_demo_accounts():
    db = SessionLocal()
    try:
        common_password_hash = hash_password("skillbridge2026")

        for acc in REQUIRED_DEMO_ACCOUNTS:
            print(f"Processing student: {acc['name']}...")
            student = db.query(Student).filter(Student.name == acc["name"]).first()
            if not student:
                student = Student(
                    name=acc["name"],
                    email=acc["email"],
                    password_hash=common_password_hash,
                    university=acc["university"],
                    graduation_year=acc["graduation_year"],
                    last_screen="dashboard",
                )
                db.add(student)
                db.flush()
                print(f" -> Created student account: {acc['name']} (ID: {student.id})")
            else:
                student.password_hash = common_password_hash
                student.university = acc["university"]
                db.flush()
                print(f" -> Found student account: {acc['name']} (ID: {student.id})")

            # Seed skills
            for sk_data in acc["skills"]:
                skill_obj = db.query(Skill).filter(Skill.name.ilike(sk_data["name"])).first()
                if not skill_obj:
                    skill_obj = Skill(
                        name=sk_data["name"],
                        category="Technical Skills",
                        description=f"Proficiency in {sk_data['name']}",
                    )
                    db.add(skill_obj)
                    db.flush()

                st_skill = db.query(StudentSkill).filter(
                    StudentSkill.student_id == student.id,
                    StudentSkill.skill_id == skill_obj.id,
                ).first()

                if not st_skill:
                    st_skill = StudentSkill(
                        student_id=student.id,
                        skill_id=skill_obj.id,
                        proficiency_level=sk_data["level"],
                        verification_status="verified",
                    )
                    db.add(st_skill)
                else:
                    st_skill.proficiency_level = sk_data["level"]
                    st_skill.verification_status = "verified"
                db.flush()

            # Seed evidence
            for ev_data in acc["evidence"]:
                existing_ev = db.query(Evidence).filter(
                    Evidence.student_id == student.id,
                    Evidence.title == ev_data["title"],
                ).first()

                if not existing_ev:
                    ev_obj = Evidence(
                        student_id=student.id,
                        evidence_type=ev_data["type"],
                        title=ev_data["title"],
                        description=ev_data["description"],
                        issuer=ev_data["issuer"],
                        evidence_url=ev_data["url"],
                        verification_status="verified",
                    )
                    db.add(ev_obj)
                    db.flush()

                    ev_skills = []
                    for s_name in ev_data["skills"]:
                        sk = db.query(Skill).filter(Skill.name.ilike(s_name)).first()
                        if sk:
                            ev_skills.append(sk)
                    ev_obj.skills = ev_skills
                    if ev_skills:
                        ev_obj.skill_id = ev_skills[0].id
                    db.flush()

        db.commit()
        print("\n[SUCCESS] All required Indian demo accounts successfully seeded into database!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_accounts()
