from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.evidence import Evidence
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.internship import Internship
from app.models.team import Team
from app.models.activity import Activity
from app.schemas.evidence import EvidenceRead

router = APIRouter(prefix="/admin", tags=["Admin & Verification"])

ADMIN_DEMO_USERNAME = "Sujal"
ADMIN_DEMO_PASSWORD = "myteam1"
ADMIN_TOKEN_SECRET = "admin-session-token-sujal-verified"


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    status: str
    token: str
    username: str
    message: str


class AdminStatsResponse(BaseModel):
    total_students: int
    pending_evidence: int
    verified_evidence: int
    total_skills: int
    total_internships: int
    total_teams: int


def verify_admin_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Validate admin authorization header."""
    if not authorization:
        # In prototype mode, allow access if header omitted or validate token
        return True
    token = authorization.replace("Bearer ", "").strip()
    if token != ADMIN_TOKEN_SECRET and token != "myteam1":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin credentials.",
        )
    return True


def sync_student_skill_from_evidence(db: Session, student_id: int, skill_id: int):
    """Dynamically sync student's StudentSkill record from verified evidence count."""
    if not skill_id or not student_id:
        return

    # Count verified evidence for this student & skill
    verified_ev_count = (
        db.query(Evidence)
        .filter(
            Evidence.student_id == student_id,
            Evidence.skill_id == skill_id,
            Evidence.verification_status == "verified",
        )
        .count()
    )

    st_skill = (
        db.query(StudentSkill)
        .filter(StudentSkill.student_id == student_id, StudentSkill.skill_id == skill_id)
        .first()
    )

    if verified_ev_count > 0:
        # Determine proficiency rank based on verified evidence count
        if verified_ev_count >= 3:
            proficiency = "Advanced"
        elif verified_ev_count == 2:
            proficiency = "Intermediate"
        else:
            proficiency = "Intermediate"

        if not st_skill:
            st_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill_id,
                proficiency_level=proficiency,
                verification_status="verified",
                verified_at=datetime.now(timezone.utc),
            )
            db.add(st_skill)
        else:
            st_skill.proficiency_level = proficiency
            st_skill.verification_status = "verified"
            st_skill.verified_at = datetime.now(timezone.utc)
    else:
        # No verified evidence
        if st_skill:
            st_skill.verification_status = "unverified"


@router.post("/login", response_model=AdminLoginResponse, summary="Admin Authentication")
def admin_login(creds: AdminLoginRequest) -> AdminLoginResponse:
    """Authenticate Admin using requested demo credentials."""
    if creds.username.strip() == ADMIN_DEMO_USERNAME and creds.password.strip() == ADMIN_DEMO_PASSWORD:
        return AdminLoginResponse(
            status="ok",
            token=ADMIN_TOKEN_SECRET,
            username=ADMIN_DEMO_USERNAME,
            message="Admin authentication successful.",
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid admin username or password.",
    )


@router.get("/evidence/pending", response_model=List[EvidenceRead], summary="Get pending verification queue")
def get_pending_evidence(
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_admin_auth),
) -> List[Evidence]:
    """Retrieve all evidence submissions waiting for admin verification."""
    return (
        db.query(Evidence)
        .options(joinedload(Evidence.skill), joinedload(Evidence.student))
        .filter(Evidence.verification_status == "pending")
        .order_by(Evidence.created_at.desc())
        .all()
    )


@router.post("/evidence/{evidence_id}/approve", response_model=EvidenceRead, summary="Approve evidence artifact")
def approve_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_admin_auth),
) -> Evidence:
    """Approve evidence submission and index the verified skill in student's passport."""
    evidence = (
        db.query(Evidence)
        .options(joinedload(Evidence.skill), joinedload(Evidence.student))
        .filter(Evidence.id == evidence_id)
        .first()
    )
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence item with ID {evidence_id} not found.",
        )

    evidence.verification_status = "verified"
    db.flush()

    # Sync StudentSkill
    if evidence.skill_id:
        sync_student_skill_from_evidence(db, evidence.student_id, evidence.skill_id)

    # Log persistent activity
    skill_name = evidence.skill.name if evidence.skill else "competency"
    activity = Activity(
        student_id=evidence.student_id,
        activity_type="verification",
        title=f"Evidence Approved: {evidence.title}",
        description=f"Admin verified your {evidence.evidence_type} artifact. {skill_name} is now a verified skill in your Digital Skill Passport.",
        icon="verified",
        related_entity_type="evidence",
        related_entity_id=evidence.id,
    )
    db.add(activity)

    db.commit()
    db.refresh(evidence)
    return evidence


@router.post("/evidence/{evidence_id}/reject", response_model=EvidenceRead, summary="Reject evidence artifact")
def reject_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_admin_auth),
) -> Evidence:
    """Reject evidence submission."""
    evidence = (
        db.query(Evidence)
        .options(joinedload(Evidence.skill), joinedload(Evidence.student))
        .filter(Evidence.id == evidence_id)
        .first()
    )
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence item with ID {evidence_id} not found.",
        )

    evidence.verification_status = "rejected"
    db.flush()

    # Sync StudentSkill
    if evidence.skill_id:
        sync_student_skill_from_evidence(db, evidence.student_id, evidence.skill_id)

    # Log persistent activity
    activity = Activity(
        student_id=evidence.student_id,
        activity_type="verification",
        title=f"Evidence Flagged: {evidence.title}",
        description=f"Evidence item was reviewed and flagged for student resubmission.",
        icon="info",
        related_entity_type="evidence",
        related_entity_id=evidence.id,
    )
    db.add(activity)

    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/stats", response_model=AdminStatsResponse, summary="Admin System Statistics")
def get_admin_stats(
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_admin_auth),
) -> AdminStatsResponse:
    """Retrieve platform statistics for Admin Dashboard."""
    total_students = db.query(Student).count()
    pending_evidence = db.query(Evidence).filter(Evidence.verification_status == "pending").count()
    verified_evidence = db.query(Evidence).filter(Evidence.verification_status == "verified").count()
    total_skills = db.query(Skill).count()
    total_internships = db.query(Internship).count()
    total_teams = db.query(Team).count()

    return AdminStatsResponse(
        total_students=total_students,
        pending_evidence=pending_evidence,
        verified_evidence=verified_evidence,
        total_skills=total_skills,
        total_internships=total_internships,
        total_teams=total_teams,
    )
