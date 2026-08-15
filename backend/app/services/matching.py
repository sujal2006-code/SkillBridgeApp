from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.internship import Internship, InternshipSkill
from app.schemas.recommendation import (
    SupportingEvidenceDetail,
    MatchedSkillDetail,
    InsufficientSkillDetail,
    UnverifiedSkillDetail,
    RecommendationRead,
    StudentRecommendationsResponse,
)

# Standard proficiency hierarchy for deterministic comparison
PROFICIENCY_RANKS: Dict[str, int] = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}


class MatchingService:
    """
    Deterministic, transparent, and fair matching engine for SkillBridge.
    
    FAIRNESS GUARANTEE:
    This service strictly evaluates verified skills, proficiency levels, and verified
    supporting evidence against job requirements. No demographic, personal, or non-skill
    attributes are used in scoring or ranking.
    """

    @classmethod
    def get_proficiency_rank(cls, level_str: Optional[str]) -> int:
        if not level_str:
            return 1
        return PROFICIENCY_RANKS.get(level_str.strip().lower(), 1)

    @classmethod
    def generate_explanation(
        cls,
        match_score: float,
        satisfied_count: int,
        total_required: int,
        matched_skills: List[MatchedSkillDetail],
        missing_skills: List[str],
        insufficient_skills: List[InsufficientSkillDetail],
        unverified_skills: List[UnverifiedSkillDetail],
    ) -> str:
        """Construct a human-readable transparent explanation of the match."""
        parts = []
        
        # 1. Overall score and required ratio
        if total_required > 0:
            parts.append(
                f"{match_score:.1f}% match. The student satisfies {satisfied_count} of {total_required} required skills."
            )
        else:
            parts.append(f"{match_score:.1f}% match based on general profile compatibility.")

        # 2. Evidence-backed matched skills
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

        # 3. Missing skills
        if missing_skills:
            if len(missing_skills) == 1:
                parts.append(f"{missing_skills[0]} is missing.")
            else:
                parts.append(f"Missing required skills: {', '.join(missing_skills)}.")
        elif total_required > 0 and not insufficient_skills and not unverified_skills:
            parts.append("All required skills are fully satisfied.")

        # 4. Insufficient proficiency skills
        if insufficient_skills:
            insufficient_notes = [
                f"{ins.skill_name} requires {ins.required_proficiency} proficiency (currently {ins.student_proficiency})"
                for ins in insufficient_skills
            ]
            parts.append(f"Proficiency gaps: {'; '.join(insufficient_notes)}.")

        # 5. Unverified skills
        if unverified_skills:
            unverified_names = [u.skill_name for u in unverified_skills]
            parts.append(f"Unverified skills awaiting review: {', '.join(unverified_names)}.")

        return " ".join(parts)

    @classmethod
    def compute_single_match(
        cls,
        student: Student,
        internship: Internship,
    ) -> RecommendationRead:
        """
        Compute deterministic match for a single (Student, Internship) pair.
        """
        # Map student verified skills by skill_id and by lowercase name
        verified_student_skills_by_id: Dict[int, StudentSkill] = {}
        unverified_student_skills_by_id: Dict[int, StudentSkill] = {}

        for ss in student.skills:
            if ss.verification_status == "verified":
                verified_student_skills_by_id[ss.skill_id] = ss
            else:
                unverified_student_skills_by_id[ss.skill_id] = ss

        # Map student verified evidence by skill_id
        verified_evidence_by_skill: Dict[int, List[SupportingEvidenceDetail]] = {}
        all_verified_evidence: List[SupportingEvidenceDetail] = []

        for ev in student.evidence:
            if ev.verification_status == "verified":
                ev_detail = SupportingEvidenceDetail.model_validate(ev)
                all_verified_evidence.append(ev_detail)
                if ev.skill_id:
                    verified_evidence_by_skill.setdefault(ev.skill_id, []).append(ev_detail)

        matched_skills: List[MatchedSkillDetail] = []
        missing_skills: List[str] = []
        insufficient_skills: List[InsufficientSkillDetail] = []
        unverified_skills: List[UnverifiedSkillDetail] = []
        
        satisfied_required_count = 0
        total_required_count = 0

        # Evaluate against internship_skills association if present
        if internship.internship_skills:
            for req_skill in internship.internship_skills:
                skill_obj = req_skill.skill
                skill_name = skill_obj.name if skill_obj else f"Skill #{req_skill.skill_id}"
                
                if req_skill.required:
                    total_required_count += 1

                # Check if student has this skill
                if req_skill.skill_id in verified_student_skills_by_id:
                    st_skill = verified_student_skills_by_id[req_skill.skill_id]
                    st_rank = cls.get_proficiency_rank(st_skill.proficiency_level)
                    req_rank = cls.get_proficiency_rank(req_skill.minimum_proficiency)
                    supporting_ev = verified_evidence_by_skill.get(req_skill.skill_id, [])

                    if st_rank >= req_rank:
                        if req_skill.required:
                            satisfied_required_count += 1
                        matched_skills.append(
                            MatchedSkillDetail(
                                skill_id=req_skill.skill_id,
                                skill_name=skill_name,
                                student_proficiency=st_skill.proficiency_level,
                                required_proficiency=req_skill.minimum_proficiency,
                                is_required=req_skill.required,
                                supporting_evidence=supporting_ev,
                            )
                        )
                    else:
                        insufficient_skills.append(
                            InsufficientSkillDetail(
                                skill_id=req_skill.skill_id,
                                skill_name=skill_name,
                                student_proficiency=st_skill.proficiency_level,
                                required_proficiency=req_skill.minimum_proficiency,
                                supporting_evidence=supporting_ev,
                            )
                        )
                elif req_skill.skill_id in unverified_student_skills_by_id:
                    unverified_skills.append(
                        UnverifiedSkillDetail(
                            skill_id=req_skill.skill_id,
                            skill_name=skill_name,
                            reason="Skill is present on student profile but has not yet been verified.",
                        )
                    )
                else:
                    if req_skill.required:
                        missing_skills.append(skill_name)
        else:
            # Fallback if required_skills list of strings is provided
            req_list = internship.required_skills or []
            total_required_count = len(req_list)
            
            # Map student skills by lowercase name
            student_skills_by_name = {
                (ss.skill.name.lower() if ss.skill else ""): ss
                for ss in student.skills
            }
            
            for req_name in req_list:
                req_lower = req_name.strip().lower()
                if req_lower in student_skills_by_name:
                    st_skill = student_skills_by_name[req_lower]
                    if st_skill.verification_status == "verified":
                        satisfied_required_count += 1
                        supporting_ev = verified_evidence_by_skill.get(st_skill.skill_id, [])
                        matched_skills.append(
                            MatchedSkillDetail(
                                skill_id=st_skill.skill_id,
                                skill_name=req_name,
                                student_proficiency=st_skill.proficiency_level,
                                required_proficiency="Intermediate",
                                is_required=True,
                                supporting_evidence=supporting_ev,
                            )
                        )
                    else:
                        unverified_skills.append(
                            UnverifiedSkillDetail(
                                skill_id=st_skill.skill_id,
                                skill_name=req_name,
                                reason="Skill is unverified.",
                            )
                        )
                else:
                    missing_skills.append(req_name)

        # Deterministic Score Formula:
        # (satisfied_required_skills / total_required_skills) * 100
        if total_required_count > 0:
            match_score = round((satisfied_required_count / total_required_count) * 100.0, 1)
        else:
            match_score = 100.0

        explanation = cls.generate_explanation(
            match_score=match_score,
            satisfied_count=satisfied_required_count,
            total_required=total_required_count,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            insufficient_skills=insufficient_skills,
            unverified_skills=unverified_skills,
        )

        return RecommendationRead(
            internship_id=internship.id,
            internship_title=internship.title,
            company=internship.company,
            location=internship.location,
            description=internship.description,
            required_skills=internship.required_skills or [],
            preferred_skills=internship.preferred_skills or [],
            match_score=match_score,
            total_required_skills=total_required_count,
            satisfied_required_skills=satisfied_required_count,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            insufficient_skills=insufficient_skills,
            unverified_skills=unverified_skills,
            evidence_support=all_verified_evidence,
            explanation=explanation,
        )

    @classmethod
    def get_recommendations_for_student(
        cls,
        db: Session,
        student_id: int,
    ) -> Optional[StudentRecommendationsResponse]:
        """
        Retrieve all available internships ranked by match score for a given student.
        """
        student = (
            db.query(Student)
            .options(
                joinedload(Student.skills).joinedload(StudentSkill.skill),
                joinedload(Student.evidence),
            )
            .filter(Student.id == student_id)
            .first()
        )
        if not student:
            return None

        internships = (
            db.query(Internship)
            .options(
                joinedload(Internship.internship_skills).joinedload(InternshipSkill.skill)
            )
            .all()
        )

        recommendations = []
        for internship in internships:
            rec = cls.compute_single_match(student, internship)
            recommendations.append(rec)

        # Order by match_score descending, then by title
        recommendations.sort(key=lambda x: (-x.match_score, x.internship_title))

        return StudentRecommendationsResponse(
            student_id=student.id,
            student_name=student.name,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
        )

    @classmethod
    def get_single_recommendation(
        cls,
        db: Session,
        student_id: int,
        internship_id: int,
    ) -> Optional[RecommendationRead]:
        """
        Retrieve a single detailed match recommendation for a specific student and internship.
        """
        student = (
            db.query(Student)
            .options(
                joinedload(Student.skills).joinedload(StudentSkill.skill),
                joinedload(Student.evidence),
            )
            .filter(Student.id == student_id)
            .first()
        )
        if not student:
            return None

        internship = (
            db.query(Internship)
            .options(
                joinedload(Internship.internship_skills).joinedload(InternshipSkill.skill)
            )
            .filter(Internship.id == internship_id)
            .first()
        )
        if not internship:
            return None

        return cls.compute_single_match(student, internship)
