from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    project_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    creator = relationship("Student", foreign_keys=[creator_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    required_skills = relationship("TeamSkillRequirement", back_populates="team", cascade="all, delete-orphan")
    invitations = relationship("TeamInvitation", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="Team Member")
    status = Column(String, nullable=False, default="invited")  # "invited", "joined", "declined"
    joined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    team = relationship("Team", back_populates="members")
    student = relationship("Student")


class TeamSkillRequirement(Base):
    __tablename__ = "team_skill_requirements"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String, nullable=True)
    minimum_proficiency = Column(String, nullable=False, default="Intermediate")
    required = Column(Boolean, nullable=False, default=True)

    # Relationships
    team = relationship("Team", back_populates="required_skills")
    skill = relationship("Skill")


class TeamInvitation(Base):
    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False, default="Team Member")
    message = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="PENDING", index=True)  # "PENDING", "ACCEPTED", "REJECTED", "CANCELLED"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    team = relationship("Team", back_populates="invitations")
    sender = relationship("Student", foreign_keys=[sender_id])
    recipient = relationship("Student", foreign_keys=[recipient_id])
