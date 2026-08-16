from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.skill import SkillRead


class EvidenceType(str, Enum):
    COURSEWORK = "coursework"
    PROJECT = "project"
    COMPETITION = "competition"
    CERTIFICATE = "certificate"
    INTERNSHIP = "internship"


class EvidenceBase(BaseModel):
    evidence_type: EvidenceType
    title: str
    description: Optional[str] = None
    issuer: Optional[str] = None
    evidence_url: Optional[str] = None
    skill_id: Optional[int] = None
    verification_status: str = "pending"


class EvidenceCreate(EvidenceBase):
    student_id: Optional[int] = None


class EvidenceRead(EvidenceBase):
    id: int
    student_id: int
    created_at: Optional[datetime] = None
    skill: Optional[SkillRead] = None

    model_config = ConfigDict(from_attributes=True)
