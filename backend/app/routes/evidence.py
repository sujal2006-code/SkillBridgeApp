from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.evidence import Evidence
from app.models.student import Student
from app.models.skill import Skill
from app.models.activity import Activity
from app.schemas.evidence import EvidenceCreate, EvidenceRead
from app.core.security import get_current_student_id, get_optional_student_id

router = APIRouter(tags=["Evidence"])


class EvidenceStatusUpdate(BaseModel):
    verification_status: str  # "verified", "pending", "rejected"


@router.post("/evidence", response_model=EvidenceRead, status_code=status.HTTP_201_CREATED)
def create_evidence(
    evidence_in: EvidenceCreate,
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> Evidence:
    """Submit new evidence item with support for normalized multiple skills."""
    student = db.query(Student).filter(Student.id == auth_student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated student not found.",
        )

    evidence_dict = evidence_in.model_dump(exclude={"skill_ids", "skill_names"})
    evidence_dict["student_id"] = auth_student_id
    evidence = Evidence(**evidence_dict)

    # Resolve all demonstrated skills (via skill_ids or skill_names or legacy skill_id)
    skills_to_link: List[Skill] = []
    seen_skill_ids = set()

    if evidence_in.skill_ids:
        for s_id in evidence_in.skill_ids:
            if s_id and s_id not in seen_skill_ids:
                sk = db.query(Skill).filter(Skill.id == s_id).first()
                if sk:
                    skills_to_link.append(sk)
                    seen_skill_ids.add(sk.id)

    if evidence_in.skill_names:
        for s_name in evidence_in.skill_names:
            s_clean = s_name.strip()
            if s_clean:
                sk = db.query(Skill).filter(Skill.name.ilike(s_clean)).first()
                if not sk:
                    sk = Skill(name=s_clean, category="General Competency", description=f"Skill in {s_clean}")
                    db.add(sk)
                    db.flush()
                if sk.id not in seen_skill_ids:
                    skills_to_link.append(sk)
                    seen_skill_ids.add(sk.id)

    if evidence_in.skill_id and evidence_in.skill_id not in seen_skill_ids:
        sk = db.query(Skill).filter(Skill.id == evidence_in.skill_id).first()
        if sk:
            skills_to_link.append(sk)
            seen_skill_ids.add(sk.id)

    # Set primary legacy skill_id to first skill if available
    if skills_to_link and not evidence.skill_id:
        evidence.skill_id = skills_to_link[0].id

    evidence.skills = skills_to_link
    db.add(evidence)
    db.flush()

    # Log persistent activity
    type_cap = evidence.evidence_type.capitalize()
    skill_names_str = ", ".join(s.name for s in skills_to_link) if skills_to_link else "skills"
    activity = Activity(
        student_id=evidence.student_id,
        activity_type="evidence_submitted",
        title=f"{type_cap} \"{evidence.title}\" submitted",
        description=f"Submitted {type_cap.lower()} demonstrating {skill_names_str} for Skill Passport verification.",
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
    """Retrieve all submitted evidence items across students with full skills relationships."""
    return (
        db.query(Evidence)
        .options(
            joinedload(Evidence.skill),
            joinedload(Evidence.skills),
            joinedload(Evidence.student),
        )
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
    """Update verification status of an evidence item and sync all associated skills."""
    evidence = (
        db.query(Evidence)
        .options(joinedload(Evidence.skills), joinedload(Evidence.skill))
        .filter(Evidence.id == evidence_id)
        .first()
    )
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence item with ID {evidence_id} not found.",
        )
    evidence.verification_status = status_update.verification_status

    # Sync all associated skills into StudentSkill table
    from app.routes.admin import sync_student_skills_for_evidence
    sync_student_skills_for_evidence(db, evidence)

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
        .options(
            joinedload(Evidence.skill),
            joinedload(Evidence.skills),
        )
        .filter(Evidence.student_id == effective_id)
        .order_by(Evidence.created_at.desc())
        .all()
    )
