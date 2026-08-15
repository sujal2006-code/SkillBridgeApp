from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.session import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    student_skills = relationship("StudentSkill", back_populates="skill", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="skill")
    internship_skills = relationship("InternshipSkill", back_populates="skill", cascade="all, delete-orphan")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    proficiency_level = Column(String(50), default="Beginner", nullable=False)
    verification_status = Column(String(50), default="unverified", nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")
