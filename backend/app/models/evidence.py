from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True, index=True)
    evidence_type = Column(String(50), nullable=False)  # coursework, project, competition, certificate, internship
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    issuer = Column(String(255), nullable=True)
    verification_status = Column(String(50), default="pending", nullable=False)  # pending, verified, rejected
    evidence_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="evidence")
    skill = relationship("Skill", back_populates="evidence")
