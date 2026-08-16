from typing import List, Optional
import time
import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
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
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    PASSWORD_VALIDATION_ERROR_MSG,
    create_access_token,
    get_current_student_id,
    get_optional_student_id,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/login", response_model=StudentLoginResponse, summary="Persistent Student Login & Registration")
def login_student(payload: StudentLoginRequest, db: Session = Depends(get_db)) -> StudentLoginResponse:
    """
    Authenticate an existing student with password verification, or register a new student account.
    Returns student profile, cryptographically signed JWT token with student ID, and last state.
    """
    # 1. Normalize identifier (strip whitespace, collapse multiple spaces)
    name_clean = " ".join(payload.name.strip().split())
    password_clean = payload.password.strip()

    if not name_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Student name is required.",
        )

    if payload.mode == "login" and not password_clean:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password is required.",
        )


    # 2. Derive email/name normalization variants for lookup
    if "@" in name_clean:
        normalized_email = name_clean.lower()
        derived_email = normalized_email
        display_name = name_clean.split("@")[0].replace(".", " ").title()
    else:
        display_name = name_clean
        base_slug = re.sub(r"[^a-zA-Z0-9]+", ".", name_clean.lower()).strip(".")
        derived_email = f"{base_slug}@skillbridge.edu"
        normalized_email = derived_email

    # 3. Lookup student by exact name, email, or normalized variants (case-insensitive)
    existing = (
        db.query(Student)
        .options(
            joinedload(Student.skills).joinedload(StudentSkill.skill),
            joinedload(Student.evidence).joinedload(Evidence.skill),
        )
        .filter(
            (func.lower(Student.name) == name_clean.lower())
            | (func.lower(Student.email) == name_clean.lower())
            | (func.lower(Student.email) == derived_email.lower())
            | (Student.name.ilike(name_clean))
            | (Student.email.ilike(name_clean))
        )
        .first()
    )

    # 4. Handle CREATE ACCOUNT / REGISTER mode
    if payload.mode == "register":
        # Validate password requirements
        is_valid_pwd, pwd_err = validate_password_strength(password_clean)
        if not is_valid_pwd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=pwd_err,
            )

        # Validate password confirmation if provided
        if payload.confirm_password is not None:
            if password_clean != payload.confirm_password.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords do not match.",
                )

        # Check duplicate account by name
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account already exists. Please log in.",
            )


        # Create new student profile in persistent PostgreSQL
        final_email = normalized_email
        if db.query(Student).filter(Student.email == final_email).first():
            final_email = f"{base_slug}.{int(time.time())}@skillbridge.edu"

        new_student = Student(
            name=display_name,
            email=final_email,
            university="SkillBridge Academic Network",
            graduation_year=2027,
            password_hash=hash_password(password_clean),
            last_screen="dashboard",
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        new_student.skills = []
        new_student.evidence = []

        token = create_access_token(new_student.id)
        return StudentLoginResponse(
            student=new_student,
            token=token,
            message=f"Account created successfully. Welcome to SkillBridge, {new_student.name}!",
            last_screen="dashboard",
        )

    # 5. Handle LOG IN mode
    if payload.mode == "login":
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incorrect name.",
            )

        # Verify password if set
        if existing.password_hash:
            if not verify_password(password_clean, existing.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password.",
                )
        else:
            # First-time password assignment for demo or seed student record
            existing.password_hash = hash_password(password_clean)
            db.commit()
            db.refresh(existing)

        token = create_access_token(existing.id)
        last_screen = existing.last_screen or "dashboard"
        return StudentLoginResponse(
            student=existing,
            token=token,
            message=f"Welcome back, {existing.name}!",
            last_screen=last_screen,
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid authentication mode. Use 'login' or 'register'.",
    )




@router.get("/me", response_model=StudentDetailRead, summary="Retrieve authenticated student profile from verified token")
def get_my_profile(
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> Student:
    """Retrieve full profile of the authenticated student using the verified JWT token directly."""
    student = (
        db.query(Student)
        .options(
            joinedload(Student.skills).joinedload(StudentSkill.skill),
            joinedload(Student.evidence).joinedload(Evidence.skill),
        )
        .filter(Student.id == auth_student_id)
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated student record not found in database.",
        )
    return student


@router.patch("/me/state", response_model=StudentRead, summary="Persist authenticated student navigation & workflow state")
def update_my_state(
    payload: StudentUpdateStateRequest,
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> Student:
    """Save the authenticated student's active screen and workflow state."""
    student = db.query(Student).filter(Student.id == auth_student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated student not found.",
        )

    if payload.last_screen is not None:
        student.last_screen = payload.last_screen
    if payload.last_state_json is not None:
        student.last_state_json = payload.last_state_json

    db.commit()
    db.refresh(student)
    return student


@router.patch("/{student_id}/state", response_model=StudentRead, summary="Persist student current navigation & workflow state")
def update_student_state(
    student_id: int,
    payload: StudentUpdateStateRequest,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> Student:
    """Save the student's active screen and workflow state to resume seamlessly."""
    if auth_student_id is not None and auth_student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot modify another student's navigation state.",
        )

    target_id = auth_student_id if auth_student_id is not None else student_id
    student = db.query(Student).filter(Student.id == target_id).first()
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
    """Find existing student by name or email, or create a fresh student profile starting at 0%."""
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
        .filter(
            (Student.name.ilike(name_clean)) | (Student.email.ilike(name_clean))
        )
        .first()
    )
    if existing:
        return existing

    import time
    if "@" in name_clean:
        email = payload.email.strip() if payload.email else name_clean.lower()
        display_name = name_clean.split("@")[0].replace(".", " ").title()
    else:
        display_name = name_clean
        base_email = name_clean.lower().replace(' ', '.')
        email = payload.email.strip() if payload.email else f"{base_email}@skillbridge.edu"
        if db.query(Student).filter(Student.email == email).first():
            email = f"{base_email}.{int(time.time())}@skillbridge.edu"

    student = Student(
        name=display_name,
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
def get_student(
    student_id: int,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> Student:
    """Retrieve a student's profile including verified skills and evidence records with authorization checks."""
    if auth_student_id is not None and auth_student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot access another student's private profile.",
        )

    effective_id = auth_student_id if auth_student_id is not None else student_id
    student = (
        db.query(Student)
        .options(
            joinedload(Student.skills).joinedload(StudentSkill.skill),
            joinedload(Student.evidence).joinedload(Evidence.skill),
        )
        .filter(Student.id == effective_id)
        .first()
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found.",
        )
    return student

