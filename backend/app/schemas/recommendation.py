from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class SupportingEvidenceDetail(BaseModel):
    id: int
    title: str
    evidence_type: str
    issuer: Optional[str] = None
    verification_status: str
    evidence_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MatchedSkillDetail(BaseModel):
    skill_id: int
    skill_name: str
    student_proficiency: str
    required_proficiency: str
    is_required: bool = True
    supporting_evidence: List[SupportingEvidenceDetail] = []


class InsufficientSkillDetail(BaseModel):
    skill_id: int
    skill_name: str
    student_proficiency: str
    required_proficiency: str
    supporting_evidence: List[SupportingEvidenceDetail] = []


class UnverifiedSkillDetail(BaseModel):
    skill_id: int
    skill_name: str
    reason: str


class RecommendationRead(BaseModel):
    internship_id: int
    internship_title: str
    company: str
    location: str
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    match_score: float
    total_required_skills: int
    satisfied_required_skills: int
    matched_skills: List[MatchedSkillDetail] = []
    missing_skills: List[str] = []
    insufficient_skills: List[InsufficientSkillDetail] = []
    unverified_skills: List[UnverifiedSkillDetail] = []
    evidence_support: List[SupportingEvidenceDetail] = []
    explanation: str


class StudentRecommendationsResponse(BaseModel):
    student_id: int
    student_name: str
    total_recommendations: int
    recommendations: List[RecommendationRead]
