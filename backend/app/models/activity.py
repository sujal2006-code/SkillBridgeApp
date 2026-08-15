from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True, index=True)
    activity_type = Column(String, nullable=False, index=True)  # "verification", "match", "team", "evidence_submitted", "application"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True, default="notifications")
    related_entity_type = Column(String, nullable=True)  # "evidence", "internship", "team", "student"
    related_entity_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    student = relationship("Student")
