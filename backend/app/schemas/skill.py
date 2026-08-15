from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillRead(SkillBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudentSkillBase(BaseModel):
    skill_id: int
    proficiency_level: str = "Beginner"
    verification_status: str = "unverified"


class StudentSkillCreate(StudentSkillBase):
    pass


class StudentSkillRead(StudentSkillBase):
    id: int
    student_id: int
    verified_at: Optional[datetime] = None
    skill: Optional[SkillRead] = None

    model_config = ConfigDict(from_attributes=True)
