from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.skill import SkillRead


class InternshipSkillBase(BaseModel):
    skill_id: int
    required: bool = True
    minimum_proficiency: str = "Intermediate"


class InternshipSkillCreate(InternshipSkillBase):
    pass


class InternshipSkillRead(InternshipSkillBase):
    id: int
    internship_id: int
    skill: Optional[SkillRead] = None

    model_config = ConfigDict(from_attributes=True)


class InternshipBase(BaseModel):
    title: str
    company: str
    description: str
    location: str
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []


class InternshipCreate(InternshipBase):
    skills_required: Optional[List[InternshipSkillCreate]] = []


class InternshipRead(InternshipBase):
    id: int
    created_at: Optional[datetime] = None
    internship_skills: List[InternshipSkillRead] = []

    model_config = ConfigDict(from_attributes=True)
