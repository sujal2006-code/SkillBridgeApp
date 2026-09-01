from typing import List, Dict, Optional, Set, Any
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models.student import Student
from app.models.skill import StudentSkill, Skill
from app.models.evidence import Evidence
from app.models.team import Team, TeamMember, TeamSkillRequirement
from app.schemas.recommendation import SupportingEvidenceDetail
from app.schemas.team import CandidateSkillContribution, TeamCandidateRecommendation


# Standard proficiency hierarchy
PROFICIENCY_RANKS: Dict[str, int] = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}

# Centralized Skill Taxonomy & Canonical Aliases
SKILL_TAXONOMY_MAP: Dict[str, str] = {
    "js": "javascript",
    "vanilla js": "javascript",
    "vanilla javascript": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    "next.js": "next.js",
    "nextjs": "next.js",
    "node.js": "node.js",
    "nodejs": "node.js",
    "html": "html",
    "html5": "html",
    "css": "css",
    "css3": "css",
    "tailwind": "tailwind css",
    "tailwind css": "tailwind css",
    "py": "python",
    "python": "python",
    "python 3": "python",
    "fastapi": "fastapi",
    "python fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "spring": "spring boot",
    "spring boot": "spring boot",
    "express": "express.js",
    "express.js": "express.js",
    "rest api": "rest api",
    "restful api": "rest api",
    "restful api design": "rest api",
    "graphql": "graphql",
    "microservices": "microservices",
    "sql": "sql",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "sql & postgresql": "postgresql",
    "mysql": "mysql",
    "mongodb": "mongodb",
    "redis": "redis",
    "database design": "database design",
    "docker": "docker",
    "cloud & docker": "docker",
    "kubernetes": "kubernetes",
    "git": "git",
    "github": "git",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "dl": "deep learning",
    "deep learning": "deep learning",
    "nlp": "nlp",
    "natural language processing": "nlp",
    "data science": "data science",
    "ds": "data science",
    "data analysis": "data analysis",
    "pandas": "pandas",
    "numpy": "numpy",
    "scikit-learn": "scikit-learn",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "generative ai": "generative ai",
    "large language models": "large language models",
    "llm": "large language models",
    "ui design": "ui design",
    "ux design": "ux design",
    "ui/ux": "ui/ux",
    "ui/ux design": "ui/ux",
    "figma": "figma",
    "wireframing": "wireframing",
    "prototyping": "prototyping",
    "c++": "c++",
    "cpp": "c++",
    "java": "java",
    "go": "go",
    "golang": "go",
    "linux": "linux",
    "aws": "aws",
    "ci/cd": "ci/cd",
    "dsa": "dsa",
    "algorithms": "algorithms",
}

# Domain categories for cross-system taxonomy resolution
DOMAIN_CATEGORIES: Dict[str, List[str]] = {
    "frontend": ["react", "vue.js", "angular", "html", "css", "javascript", "typescript", "next.js", "tailwind css", "bootstrap", "ui/ux", "figma"],
    "backend": ["fastapi", "flask", "django", "spring boot", "node.js", "express.js", "rest api", "graphql", "microservices", "python", "java", "c#", "go", "sql", "postgresql", "redis", "mongodb", "c++", "oop", "dsa"],
    "ai_ml": ["machine learning", "artificial intelligence", "deep learning", "nlp", "computer vision", "generative ai", "large language models", "data science", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy"],
    "data": ["sql", "postgresql", "mysql", "mongodb", "redis", "database design", "numpy", "pandas", "data analysis", "data visualization", "statistics", "data science"],
    "devops": ["git", "docker", "kubernetes", "aws", "azure", "google cloud", "ci/cd", "linux"],
    "ui_ux": ["ui/ux", "figma", "css", "html", "react"],
    "security": ["linux", "rest api", "sql", "dsa", "algorithms"],
}

# EXACT FIVE CORE SKILL REQUIREMENTS PER DOMAIN (Requirements 6-14)
CORE_DOMAIN_REQUIREMENTS: Dict[str, List[Dict[str, Any]]] = {
    "frontend": [
        {"id": "html", "label": "HTML", "keywords": ["html", "html5"]},
        {"id": "css", "label": "CSS", "keywords": ["css", "css3", "tailwind css", "bootstrap"]},
        {"id": "javascript", "label": "JavaScript", "keywords": ["javascript", "js", "typescript", "ts"]},
        {"id": "react", "label": "React", "keywords": ["react", "react.js", "next.js"]},
        {"id": "git", "label": "Git/GitHub", "keywords": ["git", "github"]},
    ],
    "backend": [
        {"id": "language", "label": "Programming Language", "keywords": ["python", "java", "node.js", "c#", "go", "golang", "c++", "ruby", "php"]},
        {"id": "framework", "label": "Backend Framework", "keywords": ["fastapi", "flask", "django", "spring boot", "express.js", "express", "nest.js", ".net"]},
        {"id": "api", "label": "REST/API Development", "keywords": ["rest api", "restful api", "restful api design", "graphql", "microservices"]},
        {"id": "database", "label": "Database", "keywords": ["sql", "postgresql", "mysql", "mongodb", "redis", "database design"]},
        {"id": "git", "label": "Git/GitHub", "keywords": ["git", "github"]},
    ],
    "data": [
        {"id": "sql", "label": "SQL", "keywords": ["sql", "postgresql", "mysql", "sqlite", "sql & postgresql"]},
        {"id": "db_design", "label": "Database Design", "keywords": ["database design", "data modeling", "schema design"]},
        {"id": "relational_db", "label": "Relational Database", "keywords": ["postgresql", "mysql", "sqlite", "relational database"]},
        {"id": "queries", "label": "Queries & Joins", "keywords": ["queries & joins", "sql queries", "complex joins", "advanced sql", "data analysis"]},
        {"id": "transactions", "label": "Transactions & Optimization", "keywords": ["transactions", "acid", "database optimization", "indexing", "redis"]},
    ],
    "ai_ml": [
        {"id": "python", "label": "Python", "keywords": ["python", "python 3"]},
        {"id": "numpy_pandas", "label": "NumPy/Pandas", "keywords": ["pandas", "numpy"]},
        {"id": "data_processing", "label": "Data Processing", "keywords": ["data science", "data processing", "data analysis", "feature engineering", "statistics"]},
        {"id": "machine_learning", "label": "Machine Learning", "keywords": ["machine learning", "scikit-learn", "ml algorithms"]},
        {"id": "model_eval", "label": "Model Evaluation & Deep Learning", "keywords": ["model evaluation", "deep learning", "pytorch", "tensorflow", "generative ai", "large language models", "nlp", "computer vision"]},
    ],
    "ui_ux": [
        {"id": "ui_design", "label": "UI Design", "keywords": ["ui design", "ui", "visual design"]},
        {"id": "ux_design", "label": "UX Design", "keywords": ["ux design", "ux", "user research"]},
        {"id": "figma", "label": "Figma", "keywords": ["figma", "design tool"]},
        {"id": "wireframing", "label": "Wireframing", "keywords": ["wireframing", "wireframes"]},
        {"id": "prototyping", "label": "Prototyping", "keywords": ["prototyping", "interactive prototype"]},
    ],
    "devops": [
        {"id": "linux", "label": "Linux", "keywords": ["linux", "unix", "bash"]},
        {"id": "git", "label": "Git/GitHub", "keywords": ["git", "github"]},
        {"id": "docker", "label": "Docker", "keywords": ["docker", "containerization", "containers"]},
        {"id": "cicd", "label": "CI/CD", "keywords": ["ci/cd", "continuous integration", "github actions"]},
        {"id": "cloud", "label": "Cloud Infrastructure", "keywords": ["aws", "azure", "google cloud", "cloud", "gcp", "kubernetes"]},
    ],
    "full_stack": [
        {"id": "frontend_fundamentals", "label": "HTML/CSS/JavaScript", "keywords": ["html", "css", "javascript", "typescript"]},
        {"id": "frontend_framework", "label": "React", "keywords": ["react", "react.js", "next.js"]},
        {"id": "backend_framework", "label": "Backend Framework", "keywords": ["fastapi", "express.js", "spring boot", "django", "node.js", "flask"]},
        {"id": "rest_api", "label": "REST/API Development", "keywords": ["rest api", "restful api", "restful api design", "graphql", "microservices"]},
        {"id": "database", "label": "Database", "keywords": ["sql", "postgresql", "mysql", "mongodb", "redis"]},
    ],
}

ROLE_TO_DOMAIN_KEY: Dict[str, str] = {
    "frontend": "frontend",
    "frontend developer": "frontend",
    "frontend & ui": "frontend",
    "backend": "backend",
    "backend developer": "backend",
    "data systems": "data",
    "database specialist": "data",
    "data/database specialist": "data",
    "data scientist": "data",
    "database": "data",
    "data": "data",
    "data / database": "data",
    "ml & ai": "ai_ml",
    "ai/ml developer": "ai_ml",
    "ai & ml": "ai_ml",
    "ai/ml": "ai_ml",
    "devops": "devops",
    "devops & cloud": "devops",
    "devops & cloud engineer": "devops",
    "devops engineer": "devops",
    "ui/ux": "ui_ux",
    "ui/ux designer": "ui_ux",
    "full stack": "full_stack",
    "full stack developer": "full_stack",
}

DOMAIN_DISPLAY_NAMES: Dict[str, str] = {
    "frontend": "Frontend Developer",
    "backend": "Backend Developer",
    "data": "Database Specialist",
    "ai_ml": "AI/ML Developer",
    "ui_ux": "UI/UX Designer",
    "devops": "DevOps Engineer",
    "full_stack": "Full Stack Developer",
}


def normalize_skill_name(name: str) -> str:
    """Normalize a skill string into its canonical taxonomy form."""
    clean = " ".join(name.strip().lower().split())
    return SKILL_TAXONOMY_MAP.get(clean, clean)


def are_skills_compatible(skill_a: str, skill_b: str) -> bool:
    """Determine if two skill strings refer to the same or compatible technical skill."""
    norm_a = normalize_skill_name(skill_a)
    norm_b = normalize_skill_name(skill_b)
    if norm_a == norm_b:
        return True
    if (norm_a in ["sql", "postgresql"] and norm_b in ["sql", "postgresql"]):
        return True
    if (norm_a in ["nlp", "natural language processing"] and norm_b in ["nlp", "natural language processing"]):
        return True
    if (norm_a in ["generative ai", "large language models"] and norm_b in ["generative ai", "large language models"]):
        return True
    return False


class TeamMatchingService:
    """
    Deterministic, transparent, explainable, and fair 5-core-skill team gap matching engine.
    
    FAIRNESS GUARANTEE:
    Matches candidates strictly on verified skills, team requirement gaps, and evidence artifacts.
    No demographic or protected attributes are used in matching or candidate ranking.
    """

    @classmethod
    def get_proficiency_rank(cls, level_str: Optional[str]) -> int:
        if not level_str:
            return 1
        return PROFICIENCY_RANKS.get(level_str.strip().lower(), 1)

    @classmethod
    def get_skill_domain(cls, skill_name: str) -> str:
        s_norm = normalize_skill_name(skill_name)
        for domain, core_reqs in CORE_DOMAIN_REQUIREMENTS.items():
            for req in core_reqs:
                if any(k == s_norm or k in s_norm or s_norm in k for k in req["keywords"]):
                    return domain
        return "software"

    @classmethod
    def compute_candidate_match_for_team(
        cls,
        candidate: Student,
        team_requirements: List[TeamSkillRequirement],
        covered_team_skill_ids: Set[int],
        target_role: Optional[str] = None,
        target_domain: Optional[str] = None,
    ) -> TeamCandidateRecommendation:
        """
        Evaluate candidate based on:
        1. Selected domain's 5 core requirements
        2. Candidate's verified skills satisfying each requirement
        3. Match percentage = (Fulfilled core requirements / 5) * 100%
        4. Zero verified skills in domain = Strictly 0%
        5. Detailed evidence links for fulfilled skills
        6. Explicit missing core requirements
        7. Candidate's selected professional identity
        """
        # 1. Candidate's Professional Identity
        primary_role = "Technical Contributor"
        overall_proficiency = "Intermediate"
        if hasattr(candidate, "professional_profile") and candidate.professional_profile:
            primary_role = candidate.professional_profile.primary_role or "Technical Contributor"

        # 2. Map candidate's verified skills
        candidate_verified_skills_by_name: Dict[str, StudentSkill] = {}
        candidate_verified_skills_list: List[StudentSkill] = []
        all_candidate_verified_names: List[str] = []
        candidate_domain_set: Set[str] = set()

        for ss in candidate.skills:
            if ss.verification_status == "verified" and ss.skill:
                s_name = ss.skill.name
                candidate_verified_skills_by_name[s_name.lower()] = ss
                candidate_verified_skills_list.append(ss)
                if s_name not in all_candidate_verified_names:
                    all_candidate_verified_names.append(s_name)
                candidate_domain_set.add(cls.get_skill_domain(s_name))

        # Check overall proficiency based on verified skills
        if any(ss.proficiency_level == "Advanced" for ss in candidate_verified_skills_list):
            overall_proficiency = "Advanced"
        elif any(ss.proficiency_level == "Intermediate" for ss in candidate_verified_skills_list):
            overall_proficiency = "Intermediate"
        elif candidate_verified_skills_list:
            overall_proficiency = "Beginner"
        else:
            overall_proficiency = "Proficiency not yet established"

        # Map candidate verified evidence items to skills
        verified_evidence_by_skill_name: Dict[str, List[str]] = {}
        verified_evidence_by_skill_id: Dict[int, List[SupportingEvidenceDetail]] = {}

        for ev in candidate.evidence:
            if ev.verification_status == "verified":
                ev_detail = SupportingEvidenceDetail.model_validate(ev)
                ev_title_type = f"{ev.title} ({ev.evidence_type.title()})"
                if ev.skill_id:
                    verified_evidence_by_skill_id.setdefault(ev.skill_id, []).append(ev_detail)
                if ev.skill:
                    verified_evidence_by_skill_name.setdefault(ev.skill.name.lower(), []).append(ev_title_type)
                for sk in ev.skills:
                    verified_evidence_by_skill_id.setdefault(sk.id, []).append(ev_detail)
                    verified_evidence_by_skill_name.setdefault(sk.name.lower(), []).append(ev_title_type)

        # 3. Determine target domain
        active_target = (target_role or target_domain or "").strip().lower()
        if active_target in ["all", "all roles", ""]:
            active_target = ""

        domain_key = ROLE_TO_DOMAIN_KEY.get(active_target) if active_target else None
        if not domain_key and active_target:
            for k, v in ROLE_TO_DOMAIN_KEY.items():
                if k in active_target or active_target in k:
                    domain_key = v
                    break

        if not domain_key:
            # If no target role is explicitly specified (e.g. All Roles), evaluate candidate against their OWN selected primary role
            candidate_role = primary_role.strip().lower()
            domain_key = ROLE_TO_DOMAIN_KEY.get(candidate_role)
            if not domain_key:
                for k, v in ROLE_TO_DOMAIN_KEY.items():
                    if k in candidate_role or candidate_role in k:
                        domain_key = v
                        break
            if not domain_key:
                # Fallback: infer from unfilled team requirements or first verified domain
                unfilled_domains = [
                    cls.get_skill_domain(r.skill.name)
                    for r in team_requirements
                    if r.skill and r.skill_id not in covered_team_skill_ids
                ]
                domain_key = unfilled_domains[0] if unfilled_domains else "backend"

        # Retrieve the 5 core requirements for the target domain
        core_requirements = CORE_DOMAIN_REQUIREMENTS.get(domain_key, CORE_DOMAIN_REQUIREMENTS["backend"])
        display_role = DOMAIN_DISPLAY_NAMES.get(domain_key, target_role or primary_role or "Technical Specialist")

        # 4. Evaluate candidate against the 5 core domain requirements
        fulfilled_requirements: List[str] = []
        missing_requirements: List[str] = []
        skills_contributed: List[str] = []
        evidence_breakdown: List[str] = []
        matched_contributions: List[CandidateSkillContribution] = []

        for req in core_requirements:
            req_label = req["label"]
            req_keywords = req["keywords"]

            # Search if candidate has any verified skill matching this core requirement
            matched_skill_name: Optional[str] = None
            matched_student_skill: Optional[StudentSkill] = None

            for s_name in all_candidate_verified_names:
                s_norm = normalize_skill_name(s_name)
                if any(k == s_norm or k in s_norm or s_norm in k for k in req_keywords):
                    matched_skill_name = s_name
                    matched_student_skill = candidate_verified_skills_by_name.get(s_name.lower())
                    break

            if matched_skill_name:
                fulfilled_requirements.append(f"{req_label} ({matched_skill_name})")
                if matched_skill_name not in skills_contributed:
                    skills_contributed.append(matched_skill_name)

                # Link supporting evidence
                ev_titles = verified_evidence_by_skill_name.get(matched_skill_name.lower(), [])
                first_ev = ev_titles[0] if ev_titles else "Verified Skill Passport Project"
                evidence_breakdown.append(f"{matched_skill_name} — {first_ev}")

                sk_id = matched_student_skill.skill_id if matched_student_skill else 0
                st_prof = matched_student_skill.proficiency_level if matched_student_skill else "Intermediate"
                supporting_ev = verified_evidence_by_skill_id.get(sk_id, [])

                matched_contributions.append(
                    CandidateSkillContribution(
                        skill_id=sk_id,
                        skill_name=matched_skill_name,
                        student_proficiency=st_prof,
                        required_proficiency="Intermediate",
                        is_required=True,
                        supporting_evidence=supporting_ev,
                    )
                )
            else:
                missing_requirements.append(req_label)

        # 5. Complementary Skills (Verified skills outside the core 5 domain requirements)
        core_keywords_all = [k for req in core_requirements for k in req["keywords"]]
        complementary_skills: List[str] = []
        for s_name in all_candidate_verified_names:
            s_norm = normalize_skill_name(s_name)
            if not any(k == s_norm or k in s_norm or s_norm in k for k in core_keywords_all):
                if s_name not in complementary_skills:
                    complementary_skills.append(s_name)

        # 6. Requirement Match Percentage Calculation (Exact multiples of 20%)
        # Strictly: (Fulfilled core requirements / 5) * 100%
        fulfilled_count = len(fulfilled_requirements)
        match_score = round((fulfilled_count / 5.0) * 100.0, 1)

        # STRICT ZERO RULE: If candidate has no verified skills in this domain, match_score = 0.0%
        if fulfilled_count == 0:
            match_score = 0.0

        # 7. Formulate Explainable Rationale
        if match_score == 100.0:
            explanation = (
                f"100% {display_role} Match. Candidate satisfies all 5 core requirements with verified "
                f"{', '.join(skills_contributed)}."
            )
        elif match_score > 0.0:
            missing_str = f" Missing: {', '.join(missing_requirements)}." if missing_requirements else ""
            comp_str = f" Additional verified capabilities: {', '.join(complementary_skills[:3])}." if complementary_skills else ""
            explanation = (
                f"{int(match_score)}% {display_role} Match. Fulfills {fulfilled_count} of 5 core requirements with verified "
                f"{', '.join(skills_contributed)}.{missing_str}{comp_str}"
            )
        else:
            explanation = (
                f"0% {display_role} Match. No verified {display_role} skills found in Digital Skill Passport. "
                f"Missing: {', '.join(missing_requirements)}."
            )

        # Domain tags
        domain_labels = {
            "frontend": "Frontend & UI",
            "backend": "Backend Development",
            "ai_ml": "AI & Machine Learning",
            "data": "Data Systems",
            "devops": "DevOps & Cloud",
            "ui_ux": "UI/UX",
            "full_stack": "Full Stack",
        }
        verified_domains_list = [domain_labels.get(d, d.title()) for d in candidate_domain_set]

        return TeamCandidateRecommendation(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            university=candidate.university,
            role_suggestion=primary_role,
            professional_role=primary_role,
            overall_proficiency=overall_proficiency,
            verified_domains=verified_domains_list,
            match_score=match_score,
            target_role=display_role,
            matched_skills=matched_contributions,
            skills_contributed=skills_contributed,
            complementary_skills=complementary_skills[:4],
            verified_skills=all_candidate_verified_names,
            missing_team_skills=missing_requirements,
            core_skills_fulfilled=fulfilled_requirements,
            core_skills_missing=missing_requirements,
            evidence_breakdown=evidence_breakdown,
            explanation=explanation,
        )

    @classmethod
    def get_candidate_recommendations_for_team(
        cls,
        db: Session,
        team_id: int,
        target_role: Optional[str] = None,
        target_domain: Optional[str] = None,
    ) -> List[TeamCandidateRecommendation]:
        """Retrieve explainable candidate recommendations based on team gaps and role-specific requirements."""
        team = None
        if team_id and team_id > 0:
            team = (
                db.query(Team)
                .options(
                    joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
                    joinedload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills),
                )
                .filter(Team.id == team_id)
                .first()
            )

        # 1. Identify skills already covered by joined team members
        covered_team_skill_ids: Set[int] = set()
        excluded_student_ids: Set[int] = set()

        if team:
            excluded_student_ids.add(team.creator_id)
            for member in team.members:
                if member.status == "joined":
                    excluded_student_ids.add(member.student_id)
                    if member.student:
                        for ss in member.student.skills:
                            if ss.verification_status == "verified":
                                covered_team_skill_ids.add(ss.skill_id)

        # 2. Query peer candidates
        candidates_query = (
            db.query(Student)
            .options(
                selectinload(Student.skills).joinedload(StudentSkill.skill),
                selectinload(Student.evidence).joinedload(Evidence.skill),
                selectinload(Student.evidence).selectinload(Evidence.skills),
                joinedload(Student.professional_profile),
            )
        )
        if excluded_student_ids:
            candidates_query = candidates_query.filter(Student.id.notin_(excluded_student_ids))
        candidates = candidates_query.all()

        forbidden_placeholders = {
            "alex rivera", "sarah chen", "marcus vance", "marcus young",
            "elena rostova", "priyansh sharma", "abc", "abe"
        }

        recommendations = []
        for candidate in candidates:
            if candidate.name and candidate.name.strip().lower() in forbidden_placeholders:
                continue

            # Only include candidates who have verified skills
            has_verified_skills = any(ss.verification_status == "verified" for ss in candidate.skills)
            if not has_verified_skills:
                continue

            rec = cls.compute_candidate_match_for_team(
                candidate=candidate,
                team_requirements=team.required_skills if team else [],
                covered_team_skill_ids=covered_team_skill_ids,
                target_role=target_role,
                target_domain=target_domain,
            )
            recommendations.append(rec)

        # Rank candidates by descending match score
        recommendations.sort(key=lambda r: r.match_score, reverse=True)
        return recommendations
