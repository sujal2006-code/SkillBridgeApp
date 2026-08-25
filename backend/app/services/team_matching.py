from typing import List, Dict, Optional, Set
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

# Domain classifications for complementarity detection
DOMAIN_CATEGORIES = {
    "frontend": ["react", "vue.js", "angular", "html", "css", "javascript", "typescript", "next.js", "tailwind css", "bootstrap"],
    "backend": ["fastapi", "flask", "django", "spring boot", "node.js", "express.js", "rest api", "graphql", "microservices", "python", "java", "c#", "go"],
    "ai_ml": ["machine learning", "artificial intelligence", "deep learning", "nlp", "natural language processing", "computer vision", "generative ai", "large language models", "data science", "pytorch", "tensorflow", "scikit-learn"],
    "data": ["sql", "sql & postgresql", "postgresql", "mysql", "mongodb", "redis", "database design", "numpy", "pandas", "data analysis", "data visualization", "statistics"],
    "devops": ["git", "github", "docker", "cloud & docker", "kubernetes", "aws", "azure", "google cloud", "ci/cd", "linux"],
}


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
        s_low = skill_name.lower()
        for domain, skills in DOMAIN_CATEGORIES.items():
            if any(k in s_low for k in skills):
                return domain
        return "general"

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
        3. Complementary skills (skills that add valuable domain breadth)
        4. Supporting evidence quality
        """
        # 1. Map candidate's verified skills
        candidate_verified_skills: Dict[int, StudentSkill] = {}
        all_candidate_verified_skills: List[str] = []
        for ss in candidate.skills:
            if ss.verification_status == "verified" and ss.skill:
                candidate_verified_skills[ss.skill_id] = ss
                if ss.skill.name not in all_candidate_verified_skills:
                    all_candidate_verified_skills.append(ss.skill.name)

        # If candidate has zero verified skills, return empty 0% match without fabricated skills
        if not candidate_verified_skills:
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
                missing_team_skills=[r.skill.name for r in team_requirements if r.skill and r.skill_id not in covered_team_skill_ids],
                explanation="No verified skills in Digital Skill Passport to evaluate team matching.",
            )

        # 2. Map candidate's verified evidence
        verified_evidence_by_skill: Dict[int, List[SupportingEvidenceDetail]] = {}
        for ev in candidate.evidence:
            if ev.verification_status == "verified":
                ev_detail = SupportingEvidenceDetail.model_validate(ev)
                if ev.skill_id:
                    verified_evidence_by_skill.setdefault(ev.skill_id, []).append(ev_detail)
                for sk in ev.skills:
                    verified_evidence_by_skill.setdefault(sk.id, []).append(ev_detail)

        # 3. Analyze team gaps vs candidate contributions
        matched_contributions: List[CandidateSkillContribution] = []
        skills_contributed: List[str] = []
        remaining_unfilled_gaps: List[str] = []
        
        team_unfilled_reqs = [r for r in team_requirements if r.skill_id not in covered_team_skill_ids]
        if not team_unfilled_reqs:
            team_unfilled_reqs = team_requirements

        total_gaps_count = max(1, len(team_unfilled_reqs))
        gaps_filled_by_candidate = 0

        for req in team_requirements:
            skill_obj = req.skill
            skill_name = skill_obj.name if skill_obj else f"Skill #{req.skill_id}"
            is_unfilled_gap = req.skill_id not in covered_team_skill_ids

            if req.skill_id in candidate_verified_skills:
                st_skill = candidate_verified_skills[req.skill_id]
                st_rank = cls.get_proficiency_rank(st_skill.proficiency_level)
                req_rank = cls.get_proficiency_rank(req.minimum_proficiency)

                if st_rank >= req_rank:
                    if is_unfilled_gap:
                        gaps_filled_by_candidate += 1
                    skills_contributed.append(skill_name)
                    supporting_ev = verified_evidence_by_skill.get(req.skill_id, [])
                    matched_contributions.append(
                        CandidateSkillContribution(
                            skill_id=req.skill_id,
                            skill_name=skill_name,
                            student_proficiency=st_skill.proficiency_level,
                            required_proficiency=req.minimum_proficiency,
                            is_required=req.required,
                            supporting_evidence=supporting_ev,
                        )
                    )
                else:
                    if is_unfilled_gap:
                        remaining_unfilled_gaps.append(f"{skill_name} (needs {req.minimum_proficiency})")
            else:
                if is_unfilled_gap:
                    remaining_unfilled_gaps.append(skill_name)

        # 4. Identify Complementary Skills (candidate has verified skills not in team requirements)
        team_req_skill_names = {r.skill.name.lower() for r in team_requirements if r.skill}
        
        complementary_skills: List[str] = []
        for s_name in all_candidate_verified_skills:
            if s_name not in skills_contributed and s_name.lower() not in team_req_skill_names and s_name not in complementary_skills:
                complementary_skills.append(s_name)

        # 5. Transparent Match Score Calculation:
        # - Gap fulfillment weight: 70% of score
        # - Complementarity & verified breadth: 30% of score
        gap_fill_ratio = gaps_filled_by_candidate / total_gaps_count if total_gaps_count > 0 else 0.0
        gap_score = gap_fill_ratio * 70.0
        comp_score = min(30.0, len(complementary_skills) * 7.5)
        
        raw_score = gap_score + comp_score
        match_score = min(100.0, round(raw_score, 1))

        # 6. Generate Role Suggestion
        role_suggestion = "Team Member"
        all_candidate_skills_lower = [s.lower() for s in skills_contributed + complementary_skills]
        if any("machine learning" in s or "ai" in s for s in all_candidate_skills_lower):
            role_suggestion = "ML / AI Specialist"
        elif any("react" in s or "frontend" in s or "ui" in s for s in all_candidate_skills_lower):
            role_suggestion = "Frontend & UI Engineer"
        elif any("fastapi" in s or "spring" in s or "backend" in s or "node" in s for s in all_candidate_skills_lower):
            role_suggestion = "Backend Architect"
        elif any("sql" in s or "data" in s or "database" in s or "postgres" in s for s in all_candidate_skills_lower):
            role_suggestion = "Data Systems Engineer"
        elif any("docker" in s or "aws" in s or "cloud" in s or "devops" in s for s in all_candidate_skills_lower):
            role_suggestion = "Cloud & DevOps Lead"
        elif skills_contributed:
            role_suggestion = f"{skills_contributed[0]} Specialist"

        # 7. Construct Transparent Explanation
        if skills_contributed and complementary_skills:
            explanation = (
                f"Strong match because the candidate provides {', '.join(skills_contributed)}, "
                f"which help fill the team's current skill gaps. Additional complementary capability comes from {', '.join(complementary_skills[:3])}."
            )
        elif skills_contributed:
            explanation = (
                f"Strong match because the candidate provides {', '.join(skills_contributed)}, "
                f"which help fill the team's current skill gaps."
            )
        elif complementary_skills:
            explanation = (
                f"Complementary capability match: candidate brings verified expertise in {', '.join(complementary_skills[:3])} "
                f"to expand the team's technical breadth."
            )
        else:
            explanation = "Candidate has verified skills, but does not directly match the team's current open skill requirements."

        return TeamCandidateRecommendation(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            university=candidate.university,
            role_suggestion=role_suggestion,
            match_score=match_score,
            matched_skills=matched_contributions,
            skills_contributed=skills_contributed,
            complementary_skills=complementary_skills[:5],
            verified_skills=all_candidate_verified_skills,
            missing_team_skills=remaining_unfilled_gaps,
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

        # Sort by match_score descending, then number of matched contributions, then candidate_name
        recommendations.sort(key=lambda x: (-x.match_score, -len(x.matched_skills), x.candidate_name))
        return recommendations
