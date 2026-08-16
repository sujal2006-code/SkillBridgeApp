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
    last_screen: Optional[str] = "dashboard"
    last_state_json: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StudentDetailRead(StudentRead):
    skills: List[StudentSkillRead] = []
    evidence: List[EvidenceRead] = []

    model_config = ConfigDict(from_attributes=True)


class StudentLoginRequest(BaseModel):
    name: str
    password: str
    confirm_password: Optional[str] = None
    mode: Optional[str] = "auto"  # 'login' | 'register' | 'auto'


class StudentUpdateStateRequest(BaseModel):
    last_screen: Optional[str] = None
    last_state_json: Optional[str] = None


class StudentLoginResponse(BaseModel):
    student: StudentDetailRead
    token: str
    message: str
    last_screen: str
