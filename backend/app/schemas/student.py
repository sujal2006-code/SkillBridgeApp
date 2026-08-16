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
    mode: Optional[str] = "auto"  # 'login' | 'register' | 'auto'


class StudentUpdateStateRequest(BaseModel):
    last_screen: Optional[str] = None
    last_state_json: Optional[str] = None


class StudentLoginResponse(BaseModel):
    student: StudentDetailRead
    token: str
    message: str
    last_screen: str


class RegisterOtpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: Optional[str] = None


class VerifyRegisterOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ForgotPasswordOtpRequest(BaseModel):
    email: EmailStr


class VerifyResetOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str
    confirm_password: Optional[str] = None


class ResendOtpRequest(BaseModel):
    email: EmailStr
    purpose: str = "register"  # 'register' | 'forgot_password'


class OtpResponse(BaseModel):
    message: str
    email: Optional[str] = None
    cooldown_seconds: Optional[int] = 60
    reset_token: Optional[str] = None


