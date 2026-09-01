from typing import List, Dict, Optional, Set, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.student import Student
from app.models.skill import StudentSkill, Skill
from app.models.evidence import Evidence
from app.models.professional_role import StudentProfessionalProfile
from app.services.team_matching import normalize_skill_name, DOMAIN_CATEGORIES


# Extended Platform Domain Taxonomies
PLATFORM_DOMAINS: Dict[str, List[str]] = {
    "Frontend & UI": [
        "react", "vue.js", "angular", "html", "css", "javascript", "typescript",
        "next.js", "tailwind css", "bootstrap", "ui/ux", "ui/ux design", "figma"
    ],
    "Backend Development": [
        "python", "fastapi", "flask", "django", "spring boot", "node.js", "express.js",
        "rest api", "restful api design", "graphql", "microservices", "java", "c#", "go",
        "c++", "oop", "dsa", "algorithms"
    ],
    "Data Systems & Databases": [
        "sql", "postgresql", "mysql", "mongodb", "redis", "database design",
        "pandas", "numpy", "data science", "data analysis", "data visualization",
        "statistics", "sql & postgresql"
    ],
    "AI & Machine Learning": [
        "machine learning", "artificial intelligence", "deep learning", "nlp",
        "natural language processing", "computer vision", "generative ai",
        "large language models", "pytorch", "tensorflow", "scikit-learn", "data science"
    ],
    "DevOps & Cloud": [
        "docker", "kubernetes", "aws", "azure", "google cloud", "ci/cd", "linux", "git", "github"
    ],
    "UI/UX Design": [
        "ui/ux", "ui/ux design", "figma", "css", "html", "design system"
    ],
    "Cybersecurity": [
        "linux", "rest api", "sql", "dsa", "algorithms", "network security", "cryptography"
    ],
}

# Supported Professional Roles and their Required Core Domains
ROLE_DOMAIN_REQUIREMENTS: Dict[str, Dict[str, any]] = {
    "Full Stack Developer": {
        "required_domains": ["Frontend & UI", "Backend Development"],
        "description": "Engineers end-to-end web architectures across client interfaces and backend microservices.",
        "icon": "layers",
    },
    "Frontend Developer": {
        "required_domains": ["Frontend & UI"],
        "description": "Crafts accessible, dynamic, and high-performance user interfaces and web applications.",
        "icon": "desktop_windows",
    },
    "Backend Developer": {
        "required_domains": ["Backend Development"],
        "description": "Architects resilient databases, server microservices, and high-throughput APIs.",
        "icon": "terminal",
    },
    "AI/ML Developer": {
        "required_domains": ["AI & Machine Learning"],
        "description": "Trains and deploys predictive models, deep neural networks, and generative intelligence workflows.",
        "icon": "psychology",
    },
    "Data Scientist": {
        "required_domains": ["Data Systems & Databases", "AI & Machine Learning"],
        "description": "Transforms high-dimensional data into predictive statistical intelligence and actionable models.",
        "icon": "query_stats",
    },
    "Data/Database Specialist": {
        "required_domains": ["Data Systems & Databases"],
        "description": "Designs partitioned database schemas, ETL pipelines, and high-concurrency data storage systems.",
        "icon": "database",
    },
    "DevOps & Cloud Engineer": {
        "required_domains": ["DevOps & Cloud"],
        "description": "Automates zero-downtime CI/CD deployment pipelines, container orchestration, and cloud infrastructure.",
        "icon": "cloud",
    },
    "UI/UX Designer": {
        "required_domains": ["UI/UX Design"],
        "description": "Researches user workflows, wireframes high-fidelity prototypes, and standardizes design systems.",
        "icon": "design_services",
    },
    "Cybersecurity Developer": {
        "required_domains": ["Cybersecurity"],
        "description": "Hardens REST endpoints, validates threat models, and audits codebase security vulnerabilities.",
        "icon": "security",
    },
    "Mobile Developer": {
        "required_domains": ["Frontend & UI"],
        "description": "Engineers cross-platform responsive mobile applications with smooth native interactions.",
        "icon": "smartphone",
    },
}

PROFICIENCY_WEIGHTS = {
    "expert": 4,
    "advanced": 3,
    "intermediate": 2,
    "beginner": 1,
}


class ProfessionalRoleService:
    """Service to evaluate domain proficiencies and validate evidence-backed professional identity."""

    @classmethod
    def get_skill_matched_domains(cls, skill_name: str) -> List[str]:
        s_norm = normalize_skill_name(skill_name)
        matched = []
        for domain, skills in PLATFORM_DOMAINS.items():
            if any(k == s_norm or k in s_norm or s_norm in k for k in skills):
                matched.append(domain)
        return matched

    @classmethod
    def calculate_student_domain_proficiencies(cls, student: Student) -> List[Dict]:
        """
        Evaluate a student's verified skills and supporting evidence across all platform domains.
        Returns a list of domain evaluations with genuine proficiency levels.
        Never fakes data or defaults to 'Intermediate'.
        """
        # 1. Collect all verified skills and their proficiency levels
        verified_skills_by_name: Dict[str, str] = {}
        for ss in student.skills:
            if ss.verification_status == "verified" and ss.skill:
                verified_skills_by_name[ss.skill.name] = ss.proficiency_level or "Beginner"

        # 2. Collect verified evidence artifacts count and linked skills
        verified_evidence_items = [ev for ev in student.evidence if ev.verification_status == "verified"]

        domain_results = []

        for domain_name, domain_skill_keywords in PLATFORM_DOMAINS.items():
            domain_verified_skills: List[Dict[str, str]] = []
            skill_levels: List[int] = []

            for s_name, level_str in verified_skills_by_name.items():
                s_norm = normalize_skill_name(s_name)
                if any(k == s_norm or k in s_norm or s_norm in k for k in domain_skill_keywords):
                    domain_verified_skills.append({
                        "name": s_name,
                        "level": level_str,
                    })
                    skill_levels.append(PROFICIENCY_WEIGHTS.get(level_str.lower(), 1))

            if not domain_verified_skills:
                # No verified skills in this domain
                domain_results.append({
                    "domain": domain_name,
                    "proficiency": "Proficiency not yet established",
                    "status": "unestablished",
                    "verified_skills_count": 0,
                    "verified_skills": [],
                    "evidence_count": 0,
                    "is_supported": False,
                })
                continue

            # Determine genuine proficiency from verified skills
            avg_weight = sum(skill_levels) / len(skill_levels)
            has_advanced = any(l >= 3 for l in skill_levels)
            verified_count = len(domain_verified_skills)

            # Check related evidence count for this domain
            evidence_count = 0
            for ev in verified_evidence_items:
                ev_skill_names = [s.name for s in ev.skills] if ev.skills else ([ev.skill.name] if ev.skill else [])
                for esn in ev_skill_names:
                    esn_norm = normalize_skill_name(esn)
                    if any(k == esn_norm or k in esn_norm or esn_norm in k for k in domain_skill_keywords):
                        evidence_count += 1
                        break

            # Calculate level without inventing data
            if (has_advanced or avg_weight >= 2.6) and verified_count >= 2:
                proficiency = "Advanced"
            elif avg_weight >= 1.8 or verified_count >= 2:
                proficiency = "Intermediate"
            else:
                proficiency = "Beginner"

            domain_results.append({
                "domain": domain_name,
                "proficiency": proficiency,
                "status": "verified",
                "verified_skills_count": verified_count,
                "verified_skills": [s["name"] for s in domain_verified_skills],
                "evidence_count": evidence_count,
                "is_supported": True,
            })

        return domain_results

    @classmethod
    def get_supported_roles_for_student(cls, domain_proficiencies: List[Dict]) -> List[Dict]:
        """Determine which professional roles are supported by student's verified domain evidence."""
        supported_domain_names = {
            d["domain"] for d in domain_proficiencies if d["is_supported"] and d["proficiency"] != "Proficiency not yet established"
        }

        roles_analysis = []
        for role_name, role_meta in ROLE_DOMAIN_REQUIREMENTS.items():
            req_domains = role_meta["required_domains"]
            satisfied_domains = [dom for dom in req_domains if dom in supported_domain_names]
            missing_domains = [dom for dom in req_domains if dom not in supported_domain_names]

            # Role is eligible if all required domains have verified skills
            is_supported = len(missing_domains) == 0
            
            supporting_domain_details = [
                d for d in domain_proficiencies if d["domain"] in satisfied_domains
            ]

            roles_analysis.append({
                "role": role_name,
                "description": role_meta["description"],
                "icon": role_meta["icon"],
                "is_supported": is_supported,
                "required_domains": req_domains,
                "satisfied_domains": satisfied_domains,
                "missing_domains": missing_domains,
                "supporting_evidence_domains": supporting_domain_details,
            })

        return roles_analysis

    @classmethod
    def get_or_create_student_profile(cls, db: Session, student_id: int) -> StudentProfessionalProfile:
        prof = db.query(StudentProfessionalProfile).filter(StudentProfessionalProfile.student_id == student_id).first()
        if not prof:
            prof = StudentProfessionalProfile(
                student_id=student_id,
                primary_role="Full Stack Developer",
                secondary_specializations="",
            )
            db.add(prof)
            db.commit()
            db.refresh(prof)
        return prof

    @classmethod
    def get_professional_identity(cls, db: Session, student_id: int) -> Dict:
        """Fetch comprehensive professional identity with verified domains and role eligibility."""
        student = (
            db.query(Student)
            .options(
                joinedload(Student.skills).joinedload(StudentSkill.skill),
                joinedload(Student.evidence).joinedload(Evidence.skills),
                joinedload(Student.evidence).joinedload(Evidence.skill),
                joinedload(Student.professional_profile),
            )
            .filter(Student.id == student_id)
            .first()
        )
        if not student:
            return {}

        prof = student.professional_profile
        if not prof:
            prof = cls.get_or_create_student_profile(db, student_id)

        domain_proficiencies = cls.calculate_student_domain_proficiencies(student)
        supported_roles = cls.get_supported_roles_for_student(domain_proficiencies)

        # Check if currently selected primary role is supported
        selected_role_info = next((r for r in supported_roles if r["role"] == prof.primary_role), None)
        is_role_supported = selected_role_info["is_supported"] if selected_role_info else False

        # Parse secondary specializations
        specs = [s.strip() for s in (prof.secondary_specializations or "").split(",") if s.strip()]

        # Determine overall proficiency rank
        verified_domains = [d for d in domain_proficiencies if d["is_supported"]]
        if any(d["proficiency"] == "Advanced" for d in verified_domains):
            overall_proficiency = "Advanced"
        elif any(d["proficiency"] == "Intermediate" for d in verified_domains):
            overall_proficiency = "Intermediate"
        elif verified_domains:
            overall_proficiency = "Beginner"
        else:
            overall_proficiency = "Proficiency not yet established"

        return {
            "student_id": student.id,
            "student_name": student.name,
            "university": student.university,
            "primary_role": prof.primary_role,
            "overall_proficiency": overall_proficiency,
            "is_role_supported": is_role_supported,
            "secondary_specializations": specs,
            "bio": prof.bio,
            "updated_at": prof.updated_at.isoformat() if prof.updated_at else None,
            "domain_proficiencies": domain_proficiencies,
            "supported_roles": supported_roles,
            "supported_domains_summary": [
                f"{d['domain']} — {d['proficiency']}" for d in verified_domains
            ],
        }

    @classmethod
    def update_professional_identity(
        cls,
        db: Session,
        student_id: int,
        primary_role: str,
        secondary_specializations: Optional[List[str]] = None,
        bio: Optional[str] = None,
    ) -> Dict:
        """Update student's selected professional role and secondary specializations."""
        prof = cls.get_or_create_student_profile(db, student_id)

        student = (
            db.query(Student)
            .options(
                joinedload(Student.skills).joinedload(StudentSkill.skill),
                joinedload(Student.evidence).joinedload(Evidence.skills),
            )
            .filter(Student.id == student_id)
            .first()
        )

        domain_proficiencies = cls.calculate_student_domain_proficiencies(student)
        supported_roles = cls.get_supported_roles_for_student(domain_proficiencies)

        role_info = next((r for r in supported_roles if r["role"] == primary_role), None)
        warning = None
        if role_info and not role_info["is_supported"]:
            missing_str = ", ".join(role_info["missing_domains"])
            warning = f"Role '{primary_role}' requires verified skills in {missing_str}. Your Digital Skill Passport has not yet verified artifacts in these domains."

        prof.primary_role = primary_role.strip()
        if secondary_specializations is not None:
            prof.secondary_specializations = ", ".join([s.strip() for s in secondary_specializations if s.strip()])
        if bio is not None:
            prof.bio = bio.strip()

        db.commit()
        db.refresh(prof)

        result = cls.get_professional_identity(db, student_id)
        if warning:
            result["warning"] = warning
        return result
