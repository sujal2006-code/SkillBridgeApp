from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    university = Column(String(255), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=True)
    last_screen = Column(String(50), nullable=True, default="dashboard")
    last_state_json = Column(String(2000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="student", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="student", cascade="all, delete-orphan")
    professional_profile = relationship("StudentProfessionalProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember", back_populates="student", cascade="all, delete-orphan")
