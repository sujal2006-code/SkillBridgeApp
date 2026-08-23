from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

# Many-to-many association table linking an evidence item to multiple demonstrated skills
evidence_skills = Table(
    "evidence_skills",
    Base.metadata,
    Column("evidence_id", Integer, ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    # Legacy primary skill_id preserved for backwards compatibility with existing rows
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
    skills = relationship("Skill", secondary=evidence_skills, back_populates="evidence_list")
