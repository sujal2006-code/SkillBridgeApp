from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.evidence import Evidence
from app.models.student import Student
from app.models.activity import Activity
from app.schemas.evidence import EvidenceCreate, EvidenceRead
from app.core.security import get_current_student_id, get_optional_student_id

router = APIRouter(tags=["Evidence"])


class EvidenceStatusUpdate(BaseModel):
    verification_status: str  # "verified", "pending", "rejected"


@router.post("/evidence", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
def create_evidence(
    evidence_in: EvidenceCreate,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> Evidence:
    """Submit new evidence item (coursework, project, competition, certificate, internship)."""
    # Enforce verified token identity if authenticated
    effective_student_id = auth_student_id if auth_student_id is not None else evidence_in.student_id

    student = db.query(Student).filter(Student.id == effective_student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )

    evidence_data = evidence_in.model_dump()
    evidence_data["student_id"] = effective_student_id
    evidence = Evidence(**evidence_data)
    db.add(evidence)
    db.flush()

    # Log persistent activity
    type_cap = evidence.evidence_type.capitalize()
    activity = Activity(
        student_id=evidence.student_id,
        activity_type="evidence_submitted",
        title=f"{type_cap} \"{evidence.title}\" submitted",
        description=f"Submitted {type_cap.lower()} for verification and skill passport indexing.",
        icon="upload_file",
        related_entity_type="evidence",
        related_entity_id=evidence.id,
    )
    db.add(activity)

    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/evidence", response_model=List[EvidenceRead])
def list_all_evidence(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[Evidence]:
    """Retrieve all submitted evidence items across students (for admin / verification queue)."""
    return (
        db.query(Evidence)
        .options(joinedload(Evidence.skill), joinedload(Evidence.student))
        .order_by(Evidence.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.patch("/evidence/{evidence_id}/status", response_model=EvidenceRead)
def update_evidence_status(
    evidence_id: int,
    status_update: EvidenceStatusUpdate,
    db: Session = Depends(get_db),
) -> Evidence:
    """Update verification status of an evidence item."""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence item with ID {evidence_id} not found.",
        )
    evidence.verification_status = status_update.verification_status

    # Sync StudentSkill table
    if evidence.skill_id:
        from app.routes.admin import sync_student_skill_from_evidence
        sync_student_skill_from_evidence(db, evidence.student_id, evidence.skill_id)

    # Log persistent activity
    status_title = "verified" if status_update.verification_status == "verified" else "reviewed"
    activity = Activity(
        student_id=evidence.student_id,
        activity_type="verification",
        title=f"Evidence \"{evidence.title}\" {status_title}",
        description=f"Verification status updated to {status_update.verification_status}.",
        icon="check_circle" if status_update.verification_status == "verified" else "info",
        related_entity_type="evidence",
        related_entity_id=evidence.id,
    )
    db.add(activity)

    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/students/{student_id}/evidence", response_model=List[EvidenceRead])
def list_student_evidence(
    student_id: int,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> List[Evidence]:
    """Retrieve all evidence items submitted by a specific student with token authorization checks."""
    if auth_student_id is not None and auth_student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot access another student's evidence records.",
        )

    effective_id = auth_student_id if auth_student_id is not None else student_id
    student = db.query(Student).filter(Student.id == effective_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return (
        db.query(Evidence)
        .options(joinedload(Evidence.skill))
        .filter(Evidence.student_id == effective_id)
        .order_by(Evidence.created_at.desc())
        .all()
    )

