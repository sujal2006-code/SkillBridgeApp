from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.recommendation import SupportingEvidenceDetail


# Team Skill Requirement Schemas
class TeamSkillRequirementBase(BaseModel):
    skill_id: Optional[int] = None
    skill_name: Optional[str] = None
    domain: Optional[str] = None
    minimum_proficiency: str = "Intermediate"
    required: bool = True


class TeamSkillRequirementCreate(TeamSkillRequirementBase):
    pass


class TeamSkillRequirementRead(TeamSkillRequirementBase):
    id: int
    team_id: int
    skill_name: Optional[str] = None
    domain: Optional[str] = None

    class Config:
        from_attributes = True


# Team Member Schemas
class TeamMemberBase(BaseModel):
    student_id: int
    role: str = "Team Member"
    status: str = "invited"


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberRead(TeamMemberBase):
    id: int
    team_id: int
    student_name: Optional[str] = None
    joined_at: Optional[datetime] = None
    created_at: datetime
    professional_role: Optional[str] = "Technical Contributor"
    proficiency: Optional[str] = "Intermediate"
    domains: List[str] = []
    verified_skills: List[str] = []
    evidence_items: List[str] = []

    class Config:
        from_attributes = True


# Team Invitation Schemas
class TeamInvitationCreate(BaseModel):
    recipient_id: int
    role: str = "Team Member"
    message: Optional[str] = None


class TeamInvitationRead(BaseModel):
    id: int
    team_id: int
    team_name: Optional[str] = None
    project_name: Optional[str] = None
    sender_id: int
    sender_name: Optional[str] = None
    recipient_id: int
    recipient_name: Optional[str] = None
    role: str
    message: Optional[str] = None
    status: str  # "PENDING", "ACCEPTED", "REJECTED", "CANCELLED"
    created_at: datetime
    updated_at: Optional[datetime] = None
    contributed_skills: List[str] = []

    class Config:
        from_attributes = True


class TeamInvitationAction(BaseModel):
    action: str = Field(..., description="'accept' or 'reject'")


# Team Core Schemas
class TeamCreate(BaseModel):
    name: str
    project_name: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[int] = 1
    required_skill_ids: Optional[List[int]] = None
    required_skills: Optional[List[TeamSkillRequirementCreate]] = None
    required_domains: Optional[List[str]] = None


class TeamRead(BaseModel):
    id: int
    name: str
    project_name: Optional[str] = None
    description: Optional[str] = None
    creator_id: int
    creator_name: Optional[str] = None
    created_at: datetime
    members: List[TeamMemberRead] = []
    required_skills: List[TeamSkillRequirementRead] = []
    invitations: List[TeamInvitationRead] = []
    total_members_count: int = 0
    skills_covered: List[str] = []
    skills_missing: List[str] = []
    team_coverage_percentage: float = 0.0
    domain_coverage: Dict[str, bool] = {}

    class Config:
        from_attributes = True


# Professional Profile Schemas
class StudentProfessionalProfileUpdate(BaseModel):
    primary_role: str
    secondary_specializations: Optional[List[str]] = []
    bio: Optional[str] = None


class StudentProfessionalProfileRead(BaseModel):
    student_id: int
    student_name: str
    university: Optional[str] = None
    primary_role: str
    overall_proficiency: str
    is_role_supported: bool
    secondary_specializations: List[str] = []
    bio: Optional[str] = None
    updated_at: Optional[str] = None
    domain_proficiencies: List[Dict[str, Any]] = []
    supported_roles: List[Dict[str, Any]] = []
    supported_domains_summary: List[str] = []
    warning: Optional[str] = None


# Explainable Team Candidate Recommendation Schemas
class CandidateSkillContribution(BaseModel):
    skill_id: int
    skill_name: str
    student_proficiency: str
    required_proficiency: str
    is_required: bool
    supporting_evidence: List[SupportingEvidenceDetail] = []


class TeamCandidateRecommendation(BaseModel):
    candidate_id: int
    candidate_name: str
    university: Optional[str] = None
    role_suggestion: str
    professional_role: str = "Technical Contributor"
    overall_proficiency: str = "Intermediate"
    verified_domains: List[str] = []
    match_score: float
    target_role: Optional[str] = None
    matched_skills: List[CandidateSkillContribution] = []
    skills_contributed: List[str] = []
    complementary_skills: List[str] = []
    verified_skills: List[str] = []
    missing_team_skills: List[str] = []
    core_skills_fulfilled: List[str] = []
    core_skills_missing: List[str] = []
    evidence_breakdown: List[str] = []
    explanation: str

    class Config:
        from_attributes = True
