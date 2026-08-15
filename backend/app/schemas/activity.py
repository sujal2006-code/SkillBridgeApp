from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ActivityBase(BaseModel):
    student_id: Optional[int] = None
    activity_type: str  # "verification", "match", "team", "evidence_submitted", "application"
    title: str
    description: Optional[str] = None
    icon: Optional[str] = "notifications"
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityRead(ActivityBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
