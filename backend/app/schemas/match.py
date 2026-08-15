from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.internship import InternshipRead


class MatchExplanation(BaseModel):
    verified_skills: List[str] = []
    supporting_evidence: List[Dict[str, Any]] = []
    matched_required_skills: List[str] = []
    matched_preferred_skills: List[str] = []
    missing_skills: List[str] = []


class MatchRead(BaseModel):
    id: int
    student_id: int
    internship_id: int
    match_score: float
    explanation: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    internship: Optional[InternshipRead] = None

    model_config = ConfigDict(from_attributes=True)
