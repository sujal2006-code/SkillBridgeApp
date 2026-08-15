from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class Internship(Base):
    __tablename__ = "internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    required_skills = Column(JSON, default=list, nullable=True)
    preferred_skills = Column(JSON, default=list, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    internship_skills = relationship("InternshipSkill", back_populates="internship", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="internship", cascade="all, delete-orphan")


class InternshipSkill(Base):
    __tablename__ = "internship_skills"

    id = Column(Integer, primary_key=True, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    required = Column(Boolean, default=True, nullable=False)
    minimum_proficiency = Column(String(50), default="Intermediate", nullable=False)

    # Relationships
    internship = relationship("Internship", back_populates="internship_skills")
    skill = relationship("Skill", back_populates="internship_skills")
