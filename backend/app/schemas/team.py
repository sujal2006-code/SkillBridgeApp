from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.recommendation import SupportingEvidenceDetail


# Team Skill Requirement Schemas
class TeamSkillRequirementBase(BaseModel):
    skill_id: int
    minimum_proficiency: str = "Intermediate"
    required: bool = True


class TeamSkillRequirementCreate(TeamSkillRequirementBase):
    pass


class TeamSkillRequirementRead(TeamSkillRequirementBase):
    id: int
    team_id: int
    skill_name: Optional[str] = None

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
    description: Optional[str] = None
    creator_id: int = 1
    required_skill_ids: Optional[List[int]] = None
    required_skills: Optional[List[TeamSkillRequirementCreate]] = None


class TeamRead(BaseModel):
    id: int
    name: str
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

    class Config:
        from_attributes = True


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
    match_score: float
    matched_skills: List[CandidateSkillContribution] = []
    skills_contributed: List[str] = []
    complementary_skills: List[str] = []
    missing_team_skills: List[str] = []
    explanation: str

    class Config:
        from_attributes = True
