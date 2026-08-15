from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.matching import MatchingService
from app.schemas.recommendation import StudentRecommendationsResponse, RecommendationRead
from app.models.student import Student
from app.models.internship import Internship

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Matching"])


@router.get(
    "/students/{student_id}",
    response_model=StudentRecommendationsResponse,
    summary="Get explainable internship recommendations for a student",
)
def get_student_recommendations(
    student_id: int,
    db: Session = Depends(get_db),
) -> StudentRecommendationsResponse:
    """
    Generate deterministic, transparent internship recommendations for a student.
    
    Evaluates:
    - Verified student skills
    - Supporting verified evidence (coursework, projects, competitions, certificates, internships)
    - Internship required and preferred skills
    - Minimum proficiency thresholds
    
    Returns all internships ordered by match score (highest to lowest).
    """
    # Verify student exists
    student_exists = db.query(Student).filter(Student.id == student_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )

    recommendations = MatchingService.get_recommendations_for_student(db, student_id)
    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    return recommendations


@router.get(
    "/students/{student_id}/internships/{internship_id}",
    response_model=RecommendationRead,
    summary="Get single detailed internship match explanation for a student",
)
def get_single_recommendation(
    student_id: int,
    internship_id: int,
    db: Session = Depends(get_db),
) -> RecommendationRead:
    """
    Retrieve full explainability breakdown for a specific student and internship match.
    """
    # Verify student exists
    student_exists = db.query(Student).filter(Student.id == student_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )

    # Verify internship exists
    internship_exists = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Internship with ID {internship_id} not found.",
        )

    rec = MatchingService.get_single_recommendation(db, student_id, internship_id)
    if rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match recommendation could not be calculated.",
        )
    return rec
