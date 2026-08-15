from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.skill import StudentSkillRead
from app.schemas.evidence import EvidenceRead


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    university: str
    graduation_year: int


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StudentDetailRead(StudentRead):
    skills: List[StudentSkillRead] = []
    evidence: List[EvidenceRead] = []

    model_config = ConfigDict(from_attributes=True)
