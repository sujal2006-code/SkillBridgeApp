from typing import List, Dict, Optional, Set
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models.student import Student
from app.models.skill import StudentSkill, Skill
from app.models.evidence import Evidence
from app.models.team import Team, TeamMember, TeamSkillRequirement
from app.schemas.recommendation import SupportingEvidenceDetail
from app.schemas.team import CandidateSkillContribution, TeamCandidateRecommendation


# Standard proficiency hierarchy and weights
PROFICIENCY_RANKS: Dict[str, int] = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}

PROFICIENCY_PERCENTAGES: Dict[str, float] = {
    "beginner": 50.0,
    "intermediate": 75.0,
    "advanced": 90.0,
    "expert": 98.0,
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
    "rest api": "rest api",
    "restful api": "rest api",
    "restful api design": "rest api",
    "sql": "sql",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "sql & postgresql": "postgresql",
    "mysql": "mysql",
    "mongodb": "mongodb",
    "redis": "redis",
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
    "pandas": "pandas",
    "numpy": "numpy",
    "scikit-learn": "scikit-learn",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "generative ai": "generative ai",
    "ui/ux": "ui/ux",
    "ui/ux design": "ui/ux",
    "figma": "figma",
}

# Domain classifications for complementarity detection
DOMAIN_CATEGORIES = {
    "frontend": ["react", "vue.js", "angular", "html", "css", "javascript", "typescript", "next.js", "tailwind css", "bootstrap", "ui/ux", "figma"],
    "backend": ["fastapi", "flask", "django", "spring boot", "node.js", "express.js", "rest api", "graphql", "microservices", "python", "java", "c#", "go", "sql", "postgresql", "redis", "mongodb"],
    "ai_ml": ["machine learning", "artificial intelligence", "deep learning", "nlp", "computer vision", "generative ai", "data science", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy"],
    "data": ["sql", "postgresql", "mysql", "mongodb", "redis", "database design", "numpy", "pandas", "data analysis", "data visualization", "statistics", "data science"],
    "devops": ["git", "docker", "kubernetes", "aws", "azure", "google cloud", "ci/cd", "linux"],
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
    # Compatibility between generic SQL and specific relational engines
    if (norm_a in ["sql", "postgresql"] and norm_b in ["sql", "postgresql"]):
        return True
    return False


class TeamMatchingService:
    """
    Deterministic, transparent, explainable, and fair team candidate recommendation engine.
    
    FAIRNESS GUARANTEE:
    Evaluates candidate students strictly on verified skills, team gap complementarity,
    proficiency levels, and supporting evidence. No demographic or protected attributes
    are used in matching or ranking.
    """

    @classmethod
    def get_proficiency_rank(cls, level_str: Optional[str]) -> int:
        if not level_str:
            return 1
        return PROFICIENCY_RANKS.get(level_str.strip().lower(), 1)

    @classmethod
    def get_skill_domain(cls, skill_name: str) -> str:
        s_norm = normalize_skill_name(skill_name)
        for domain, skills in DOMAIN_CATEGORIES.items():
            if any(k in s_norm or s_norm in k for k in skills):
                return domain
        return "software"

    @classmethod
    def compute_candidate_match_for_team(
        cls,
        candidate: Student,
        team_requirements: List[TeamSkillRequirement],
        covered_team_skill_ids: Set[int],
    ) -> TeamCandidateRecommendation:
        """
        Evaluate candidate based on:
        1. Current missing team skills (the team's unfilled gaps)
        2. Candidate's verified skill contributions to missing gaps
        3. Proficiency depth of verified skills
        4. Complementary skills (verified skills adding valuable domain breadth)
        5. Supporting evidence quality
        """
        # 1. Map candidate's verified skills
        candidate_verified_skills_by_id: Dict[int, StudentSkill] = {}
        candidate_verified_skills_list: List[StudentSkill] = []
        all_candidate_verified_names: List[str] = []

        for ss in candidate.skills:
            if ss.verification_status == "verified" and ss.skill:
                candidate_verified_skills_by_id[ss.skill_id] = ss
                candidate_verified_skills_list.append(ss)
                if ss.skill.name not in all_candidate_verified_names:
                    all_candidate_verified_names.append(ss.skill.name)

        # 0 Verified Skills Protection
        if not candidate_verified_skills_list:
            missing_skills = [
                r.skill.name for r in team_requirements
                if r.skill and r.skill_id not in covered_team_skill_ids
            ]
            return TeamCandidateRecommendation(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                university=candidate.university,
                role_suggestion="Student",
                match_score=0.0,
                matched_skills=[],
                skills_contributed=[],
                complementary_skills=[],
                verified_skills=[],
                missing_team_skills=missing_skills,
                explanation="No verified skills in Digital Skill Passport to evaluate team matching.",
            )

        # 2. Map candidate's verified evidence
        verified_evidence_by_skill_id: Dict[int, List[SupportingEvidenceDetail]] = {}
        for ev in candidate.evidence:
            if ev.verification_status == "verified":
                ev_detail = SupportingEvidenceDetail.model_validate(ev)
                if ev.skill_id:
                    verified_evidence_by_skill_id.setdefault(ev.skill_id, []).append(ev_detail)
                for sk in ev.skills:
                    verified_evidence_by_skill_id.setdefault(sk.id, []).append(ev_detail)

        # 3. Analyze team gaps vs candidate contributions
        matched_contributions: List[CandidateSkillContribution] = []
        skills_contributed: List[str] = []
        missing_team_skills: List[str] = []

        # Determine target team requirements (unfilled gaps prioritized)
        team_unfilled_reqs = [r for r in team_requirements if r.skill_id not in covered_team_skill_ids]
        if not team_unfilled_reqs:
            team_unfilled_reqs = team_requirements

        total_reqs_count = max(1, len(team_requirements))
        gaps_filled_by_candidate = 0
        matched_proficiency_ranks: List[int] = []

        for req in team_requirements:
            req_skill_obj = req.skill
            req_skill_name = req_skill_obj.name if req_skill_obj else f"Skill #{req.skill_id}"
            is_unfilled_gap = req.skill_id not in covered_team_skill_ids

            # Find matching candidate skill by ID or taxonomy compatibility
            matched_st_skill = candidate_verified_skills_by_id.get(req.skill_id)
            if not matched_st_skill:
                for ss in candidate_verified_skills_list:
                    if ss.skill and are_skills_compatible(ss.skill.name, req_skill_name):
                        matched_st_skill = ss
                        break

            if matched_st_skill and matched_st_skill.skill:
                st_rank = cls.get_proficiency_rank(matched_st_skill.proficiency_level)
                req_rank = cls.get_proficiency_rank(req.minimum_proficiency)
                matched_proficiency_ranks.append(st_rank)

                if st_rank >= req_rank:
                    if is_unfilled_gap:
                        gaps_filled_by_candidate += 1
                    if req_skill_name not in skills_contributed:
                        skills_contributed.append(req_skill_name)
                    
                    supporting_ev = verified_evidence_by_skill_id.get(matched_st_skill.skill_id, [])
                    matched_contributions.append(
                        CandidateSkillContribution(
                            skill_id=req.skill_id,
                            skill_name=req_skill_name,
                            student_proficiency=matched_st_skill.proficiency_level,
                            required_proficiency=req.minimum_proficiency,
                            is_required=req.required,
                            supporting_evidence=supporting_ev,
                        )
                    )
                else:
                    if is_unfilled_gap and req_skill_name not in missing_team_skills:
                        missing_team_skills.append(f"{req_skill_name} (needs {req.minimum_proficiency})")
            else:
                if is_unfilled_gap and req_skill_name not in missing_team_skills:
                    missing_team_skills.append(req_skill_name)

        # 4. Identify Complementary Skills (candidate verified skills not required by the team)
        team_req_names = [r.skill.name for r in team_requirements if r.skill]
        complementary_skills: List[str] = []

        for s_name in all_candidate_verified_names:
            is_already_matched = any(are_skills_compatible(s_name, req_name) for req_name in team_req_names)
            if not is_already_matched and s_name not in complementary_skills:
                complementary_skills.append(s_name)

        # 5. Deterministic & Transparent Match Score Calculation
        # - Required Gaps Fulfillment: Up to 70.0 points
        # - Proficiency Factor for matched skills: Up to 15.0 points
        # - Complementary Domain Breadth: Up to 15.0 points
        gap_fill_ratio = len(skills_contributed) / total_reqs_count if total_reqs_count > 0 else 0.0
        gap_score = gap_fill_ratio * 70.0

        prof_score = 0.0
        if matched_proficiency_ranks:
            avg_rank = sum(matched_proficiency_ranks) / len(matched_proficiency_ranks)
            # Rank 1: 5pts, Rank 2: 9pts, Rank 3: 12pts, Rank 4: 15pts
            prof_score = min(15.0, (avg_rank / 4.0) * 15.0)

        comp_score = min(15.0, len(complementary_skills) * 3.0)

        raw_score = gap_score + prof_score + comp_score
        
        # If no direct requirements matched but candidate has strong domain complementarity
        if len(skills_contributed) == 0:
            # Check domain overlap with team requirements
            team_domains = {cls.get_skill_domain(r.skill.name) for r in team_requirements if r.skill}
            candidate_domains = {cls.get_skill_domain(s) for s in all_candidate_verified_names}
            domain_overlap = team_domains.intersection(candidate_domains)
            if domain_overlap:
                raw_score = min(25.0, comp_score + (len(domain_overlap) * 5.0))
            else:
                raw_score = min(15.0, comp_score * 0.5)

        match_score = min(100.0, max(0.0, round(raw_score, 1)))

        # 6. Generate Realistic Role Suggestion
        role_suggestion = "Technical Contributor"
        all_skills_combined = [s.lower() for s in skills_contributed + complementary_skills]
        if any(k in all_skills_combined for k in ["react", "html", "css", "javascript", "typescript", "ui/ux", "figma"]):
            if any(k in all_skills_combined for k in ["fastapi", "python", "node.js", "sql", "postgresql"]):
                role_suggestion = "Full Stack Developer"
            else:
                role_suggestion = "Frontend Developer"
        elif any(k in all_skills_combined for k in ["fastapi", "python", "node.js", "django", "microservices"]):
            role_suggestion = "Backend Developer"
        elif any(k in all_skills_combined for k in ["machine learning", "deep learning", "pytorch", "nlp"]):
            role_suggestion = "AI/ML Engineer"
        elif any(k in all_skills_combined for k in ["pandas", "numpy", "data science", "data visualization", "sql"]):
            role_suggestion = "Data Scientist"
        elif any(k in all_skills_combined for k in ["docker", "kubernetes", "aws", "git", "ci/cd"]):
            role_suggestion = "DevOps & Cloud Engineer"
        elif skills_contributed:
            role_suggestion = f"{skills_contributed[0]} Specialist"

        # 7. Construct Dynamic, Explainable Rationale
        primary_domain = cls.get_skill_domain(skills_contributed[0]) if skills_contributed else "technical"

        if match_score >= 75.0:
            comp_text = f" Their additional {', '.join(complementary_skills[:3])} capabilities provide complementary {primary_domain} depth." if complementary_skills else ""
            explanation = (
                f"Strong match because the candidate fills {len(skills_contributed)} of the team's {total_reqs_count} priority skill gaps with verified {', '.join(skills_contributed)} expertise.{comp_text}"
            )
        elif match_score >= 50.0:
            missing_text = f" Main missing requirements are {', '.join(missing_team_skills[:2])}." if missing_team_skills else ""
            comp_text = f" Additional verified {', '.join(complementary_skills[:2])} add valuable technical breadth." if complementary_skills else ""
            explanation = (
                f"Good match because the candidate satisfies team requirements with verified {', '.join(skills_contributed)}.{missing_text}{comp_text}"
            )
        elif match_score >= 25.0:
            skills_active = skills_contributed if skills_contributed else complementary_skills[:2]
            missing_text = f", but currently lacks verified {', '.join(missing_team_skills[:3])} experience" if missing_team_skills else ""
            explanation = (
                f"Moderate match because the candidate has verified {', '.join(skills_active)} skills that partially overlap with the team's requirements{missing_text}."
            )
        else:
            missing_text = f" The main missing skills are {', '.join(missing_team_skills[:3])}." if missing_team_skills else ""
            explanation = (
                f"Lower match because the candidate currently has limited overlap with the team's required technical skills.{missing_text}"
            )

        return TeamCandidateRecommendation(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            university=candidate.university,
            role_suggestion=role_suggestion,
            match_score=match_score,
            matched_skills=matched_contributions,
            skills_contributed=skills_contributed,
            complementary_skills=complementary_skills[:5],
            verified_skills=all_candidate_verified_names,
            missing_team_skills=missing_team_skills,
            explanation=explanation,
        )

    @classmethod
    def get_candidate_recommendations_for_team(
        cls,
        db: Session,
        team_id: int,
    ) -> List[TeamCandidateRecommendation]:
        """Retrieve candidate recommendations based on verified skill complementarity and team gaps."""
        team = (
            db.query(Team)
            .options(
                joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
                joinedload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills),
            )
            .filter(Team.id == team_id)
            .first()
        )
        if not team:
            return []

        # 1. Identify skills already covered by joined team members
        covered_team_skill_ids: Set[int] = set()
        excluded_student_ids = {team.creator_id}

        for member in team.members:
            excluded_student_ids.add(member.student_id)
            if member.status == "joined" and member.student:
                for ss in member.student.skills:
                    if ss.verification_status == "verified":
                        covered_team_skill_ids.add(ss.skill_id)

        # 2. Query peer candidates efficiently using selectinload
        candidates = (
            db.query(Student)
            .options(
                selectinload(Student.skills).joinedload(StudentSkill.skill),
                selectinload(Student.evidence).joinedload(Evidence.skill),
                selectinload(Student.evidence).selectinload(Evidence.skills),
            )
            .filter(Student.id.notin_(excluded_student_ids))
            .all()
        )

        recommendations = []
        for candidate in candidates:
            # Only include candidates who have verified skills in their passport
            has_verified_skills = any(ss.verification_status == "verified" for ss in candidate.skills)
            if not has_verified_skills:
                continue

            rec = cls.compute_candidate_match_for_team(
                candidate=candidate,
                team_requirements=team.required_skills,
                covered_team_skill_ids=covered_team_skill_ids,
            )
            recommendations.append(rec)

        # Rank candidates by descending match score
        recommendations.sort(key=lambda r: r.match_score, reverse=True)
        return recommendations
