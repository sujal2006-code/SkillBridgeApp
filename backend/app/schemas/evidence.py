from typing import Optional, List
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
    skill_ids: Optional[List[int]] = None
    skill_names: Optional[List[str]] = None


class EvidenceRead(EvidenceBase):
    id: int
    student_id: int
    created_at: Optional[datetime] = None
    skill: Optional[SkillRead] = None
    skills: List[SkillRead] = []

    model_config = ConfigDict(from_attributes=True)
