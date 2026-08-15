from typing import List, Dict, Optional
from sqlalchemy.orm import Session, joinedload
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


class TeamMatchingService:
    """
    Deterministic, transparent, and fair team candidate recommendation engine.
    
    FAIRNESS GUARANTEE:
    Evaluates candidate students strictly on verified skills, proficiency levels, and
    supporting evidence against team skill requirements. No demographic or non-skill
    attributes (gender, ethnicity, religion, age, university prestige) are used in ranking.
    """

    @classmethod
    def get_proficiency_rank(cls, level_str: Optional[str]) -> int:
        if not level_str:
            return 1
        return PROFICIENCY_RANKS.get(level_str.strip().lower(), 1)

    @classmethod
    def generate_candidate_explanation(
        cls,
        candidate_name: str,
        match_score: float,
        satisfied_count: int,
        total_required: int,
        matched_skills: List[CandidateSkillContribution],
        missing_skills: List[str],
    ) -> str:
        """Construct transparent, human-readable match explanation for team candidate."""
        parts = []

        if total_required > 0:
            parts.append(
                f"{match_score:.1f}% match. {candidate_name} satisfies {satisfied_count} of {total_required} team skill requirements."
            )
        else:
            parts.append(f"{match_score:.1f}% match based on general technical competence.")

        if matched_skills:
            evidence_sentences = []
            for ms in matched_skills:
                if ms.supporting_evidence:
                    types = list(dict.fromkeys(e.evidence_type for e in ms.supporting_evidence))
                    type_str = " and ".join(types)
                    evidence_sentences.append(f"{ms.skill_name} is supported by verified {type_str}")
                else:
                    evidence_sentences.append(f"{ms.skill_name} is verified at {ms.student_proficiency} proficiency")

            if len(evidence_sentences) == 1:
                parts.append(f"{evidence_sentences[0]}.")
            elif len(evidence_sentences) > 1:
                joined = ", ".join(evidence_sentences[:-1]) + f", and {evidence_sentences[-1]}."
                parts.append(joined)

        if missing_skills:
            parts.append(f"Remaining team skills to fill: {', '.join(missing_skills)}.")
        elif total_required > 0:
            parts.append("All team skill requirements are satisfied by this candidate.")

        return " ".join(parts)

    @classmethod
    def compute_candidate_match_for_team(
        cls,
        candidate: Student,
        team_requirements: List[TeamSkillRequirement],
    ) -> TeamCandidateRecommendation:
        """Evaluate a single student candidate against a team's skill requirements."""
        # 1. Map candidate's verified skills
        verified_skills_by_id: Dict[int, StudentSkill] = {}
        for ss in candidate.skills:
            if ss.verification_status == "verified":
                verified_skills_by_id[ss.skill_id] = ss

        # 2. Map candidate's verified evidence
        verified_evidence_by_skill: Dict[int, List[SupportingEvidenceDetail]] = {}
        for ev in candidate.evidence:
            if ev.verification_status == "verified" and ev.skill_id:
                ev_detail = SupportingEvidenceDetail.model_validate(ev)
                verified_evidence_by_skill.setdefault(ev.skill_id, []).append(ev_detail)

        matched_skills: List[CandidateSkillContribution] = []
        skills_contributed: List[str] = []
        missing_team_skills: List[str] = []
        satisfied_count = 0
        total_required_count = len(team_requirements)

        for req in team_requirements:
            skill_obj = req.skill
            skill_name = skill_obj.name if skill_obj else f"Skill #{req.skill_id}"

            if req.skill_id in verified_skills_by_id:
                st_skill = verified_skills_by_id[req.skill_id]
                st_rank = cls.get_proficiency_rank(st_skill.proficiency_level)
                req_rank = cls.get_proficiency_rank(req.minimum_proficiency)

                if st_rank >= req_rank:
                    satisfied_count += 1
                    skills_contributed.append(skill_name)
                    supporting_ev = verified_evidence_by_skill.get(req.skill_id, [])
                    matched_skills.append(
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
                    missing_team_skills.append(f"{skill_name} (needs {req.minimum_proficiency})")
            else:
                missing_team_skills.append(skill_name)

        if total_required_count > 0:
            match_score = round((satisfied_count / total_required_count) * 100.0, 1)
        else:
            match_score = 100.0 if len(verified_skills_by_id) > 0 else 50.0

        # Infer suitable team role suggestion based on matched skills
        role_suggestion = "Team Member"
        if any("machine learning" in s.lower() or "ai" in s.lower() for s in skills_contributed):
            role_suggestion = "ML / AI Engineer"
        elif any("react" in s.lower() or "frontend" in s.lower() for s in skills_contributed):
            role_suggestion = "UI / Frontend Developer"
        elif any("fastapi" in s.lower() or "python" in s.lower() for s in skills_contributed):
            role_suggestion = "Backend Engineer"
        elif any("sql" in s.lower() or "database" in s.lower() for s in skills_contributed):
            role_suggestion = "Data Engineer"
        elif skills_contributed:
            role_suggestion = f"{skills_contributed[0]} Specialist"

        explanation = cls.generate_candidate_explanation(
            candidate_name=candidate.name,
            match_score=match_score,
            satisfied_count=satisfied_count,
            total_required=total_required_count,
            matched_skills=matched_skills,
            missing_skills=missing_team_skills,
        )

        return TeamCandidateRecommendation(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            university=candidate.university,
            role_suggestion=role_suggestion,
            match_score=match_score,
            matched_skills=matched_skills,
            skills_contributed=skills_contributed,
            missing_team_skills=missing_team_skills,
            explanation=explanation,
        )

    @classmethod
    def get_candidate_recommendations_for_team(
        cls,
        db: Session,
        team_id: int,
    ) -> List[TeamCandidateRecommendation]:
        """Retrieve candidate recommendations from DB for a given team."""
        team = (
            db.query(Team)
            .options(
                joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
                joinedload(Team.members),
            )
            .filter(Team.id == team_id)
            .first()
        )
        if not team:
            return []

        # Exclude creator and current team members
        excluded_student_ids = {team.creator_id}
        for member in team.members:
            excluded_student_ids.add(member.student_id)

        # Query candidate students
        candidates = (
            db.query(Student)
            .options(
                joinedload(Student.skills).joinedload(StudentSkill.skill),
                joinedload(Student.evidence),
            )
            .filter(Student.id.notin_(excluded_student_ids))
            .all()
        )

        recommendations = []
        for candidate in candidates:
            rec = cls.compute_candidate_match_for_team(candidate, team.required_skills)
            recommendations.append(rec)

        # Sort by match_score descending, then candidate_name
        recommendations.sort(key=lambda x: (-x.match_score, x.candidate_name))

        return recommendations
