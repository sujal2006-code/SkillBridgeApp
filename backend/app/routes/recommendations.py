from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.matching import MatchingService
from app.schemas.recommendation import StudentRecommendationsResponse, RecommendationRead
from app.models.student import Student
from app.models.internship import Internship
from app.core.security import get_current_student_id, get_optional_student_id

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Matching"])


@router.get(
    "/me",
    response_model=StudentRecommendationsResponse,
    summary="Get explainable internship recommendations for the authenticated student",
)
def get_my_recommendations(
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> StudentRecommendationsResponse:
    """
    Generate deterministic, transparent internship recommendations directly for the
    authenticated student using their verified JWT token identity.
    """
    # Verify student exists in PostgreSQL
    student_exists = db.query(Student).filter(Student.id == auth_student_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated student not found.",
        )

    recommendations = MatchingService.get_recommendations_for_student(db, auth_student_id)
    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return recommendations


@router.get(
    "/students/{student_id}",
    response_model=StudentRecommendationsResponse,
    summary="Get explainable internship recommendations for a student",
)
def get_student_recommendations(
    student_id: int,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> StudentRecommendationsResponse:
    """
    Generate deterministic, transparent internship recommendations for a student.
    Enforces that authenticated students can only view their own recommendation matches.
    """
    if auth_student_id is not None and auth_student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot view recommendations for another student.",
        )

    effective_id = auth_student_id if auth_student_id is not None else student_id

    # Verify student exists in PostgreSQL
    student_exists = db.query(Student).filter(Student.id == effective_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {effective_id} not found.",
        )

    recommendations = MatchingService.get_recommendations_for_student(db, effective_id)
    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {effective_id} not found.",
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
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> RecommendationRead:
    """
    Retrieve full explainability breakdown for a specific student and internship match.
    Enforces authorization check against the verified token.
    """
    if auth_student_id is not None and auth_student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot view match explanations for another student.",
        )

    effective_id = auth_student_id if auth_student_id is not None else student_id

    # Verify student exists
    student_exists = db.query(Student).filter(Student.id == effective_id).first()
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {effective_id} not found.",
        )

    # Verify internship exists
    internship_exists = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Internship with ID {internship_id} not found.",
        )

    rec = MatchingService.get_single_recommendation(db, effective_id, internship_id)
    if rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match recommendation could not be calculated.",
        )
    return rec

