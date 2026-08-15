from typing import List, Optional
import time
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.student import Student
from app.models.skill import StudentSkill
from app.models.evidence import Evidence
from app.schemas.student import (
    StudentCreate,
    StudentRead,
    StudentDetailRead,
    StudentLoginRequest,
    StudentLoginResponse,
    StudentUpdateStateRequest,
)
from app.core.security import hash_password, verify_password, generate_session_token

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/login", response_model=StudentLoginResponse, summary="Persistent Student Login & Registration")
def login_student(payload: StudentLoginRequest, db: Session = Depends(get_db)) -> StudentLoginResponse:
    """
    Authenticate an existing student with password verification, or register a new student account.
    Returns student profile, authentication token, and their last discontinued screen/state.
    """
    name_clean = payload.name.strip()
    password_clean = payload.password.strip()

    if not name_clean or not password_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both student name and password are required.",
        )

    # Lookup student by name (case-insensitive)
    existing = (
        db.query(Student)
        .options(
            joinedload(Student.skills).joinedload(StudentSkill.skill),
            joinedload(Student.evidence).joinedload(Evidence.skill),
        )
        .filter(Student.name.ilike(name_clean))
        .first()
    )

    if existing:
        # If explicitly registering and account already has password, return error
        if payload.mode == "register" and existing.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account for '{existing.name}' already exists. Please choose 'Log In' instead.",
            )

        # Verify password if already set
        if existing.password_hash:
            if not verify_password(password_clean, existing.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Incorrect password for account '{existing.name}'. Please try again.",
                )
        else:
            # First-time password assignment for existing or seed student record
            existing.password_hash = hash_password(password_clean)
            db.commit()
            db.refresh(existing)

        token = generate_session_token()
        last_screen = existing.last_screen or "dashboard"
        return StudentLoginResponse(
            student=existing,
            token=token,
            message=f"Welcome back, {existing.name}!",
            last_screen=last_screen,
        )

    # If student does not exist
    if payload.mode == "login":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found for '{name_clean}'. Please select 'Create Account' to register.",
        )

    # Create new student profile
    base_email = name_clean.lower().replace(" ", ".")
    email = f"{base_email}@skillbridge.edu"
    if db.query(Student).filter(Student.email == email).first():
        email = f"{base_email}.{int(time.time())}@skillbridge.edu"

    new_student = Student(
        name=name_clean,
        email=email,
        university="SkillBridge Academic Network",
        graduation_year=2027,
        password_hash=hash_password(password_clean),
        last_screen="dashboard",
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Load relationships
    new_student.skills = []
    new_student.evidence = []

    token = generate_session_token()
    return StudentLoginResponse(
        student=new_student,
        token=token,
        message=f"Account created successfully. Welcome to SkillBridge, {new_student.name}!",
        last_screen="dashboard",
    )


@router.patch("/{student_id}/state", response_model=StudentRead, summary="Persist student current navigation & workflow state")
def update_student_state(
    student_id: int, payload: StudentUpdateStateRequest, db: Session = Depends(get_db)
) -> Student:
    """Save the student's active screen and workflow state to resume seamlessly."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )

    if payload.last_screen is not None:
        student.last_screen = payload.last_screen
    if payload.last_state_json is not None:
        student.last_state_json = payload.last_state_json

    db.commit()
    db.refresh(student)
    return student



class StudentOnboardRequest(BaseModel):
    name: str
    email: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = 2027


@router.post("/onboard", response_model=StudentDetailRead, summary="Onboard or retrieve student by name")
def onboard_student(payload: StudentOnboardRequest, db: Session = Depends(get_db)) -> Student:
    """Find existing student by name or create a fresh student profile starting at 0%."""
    name_clean = payload.name.strip()
    if not name_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Student name is required.",
        )

    existing = (
        db.query(Student)
        .options(
            joinedload(Student.skills).joinedload(StudentSkill.skill),
            joinedload(Student.evidence).joinedload(Evidence.skill),
        )
        .filter(Student.name.ilike(name_clean))
        .first()
    )
    if existing:
        return existing

    import time
    base_email = name_clean.lower().replace(' ', '.')
    email = payload.email.strip() if payload.email else f"{base_email}@skillbridge.edu"
    if db.query(Student).filter(Student.email == email).first():
        email = f"{base_email}.{int(time.time())}@skillbridge.edu"

    student = Student(
        name=name_clean,
        email=email,
        university=payload.university or "SkillBridge Academic Network",
        graduation_year=payload.graduation_year or 2027,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)) -> Student:
    """Register a new student."""
    existing = db.query(Student).filter(Student.email == student_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A student with this email already exists.",
        )
    student = Student(**student_in.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("", response_model=List[StudentRead])
def list_students(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)) -> List[Student]:
    """Retrieve list of students."""
    return db.query(Student).offset(skip).limit(limit).all()


@router.get("/{student_id}", response_model=StudentDetailRead)
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    """Retrieve a student's profile including verified skills and evidence records."""
    student = (
        db.query(Student)
        .options(
            joinedload(Student.skills).joinedload(StudentSkill.skill),
            joinedload(Student.evidence).joinedload(Evidence.skill),
        )
        .filter(Student.id == student_id)
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return student
