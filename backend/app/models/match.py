from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class Match(Base):
    """
    Explainable match representation between a Student and an Internship.
    
    FAIRNESS GUARANTEE:
    Matching strictly evaluates verified skill proficiencies, supporting evidence,
    and requirements without any demographic or protected attributes.
    """
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    internship_id = Column(Integer, ForeignKey("internships.id"), nullable=False, index=True)
    match_score = Column(Float, nullable=False)
    # Explainability payload: {verified_skills: [], supporting_evidence: [], matched_required: [], matched_preferred: [], missing_skills: []}
    explanation = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="matches")
    internship = relationship("Internship", back_populates="matches")
