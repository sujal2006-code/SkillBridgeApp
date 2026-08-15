from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.student import Student
from app.models.skill import StudentSkill
from app.models.evidence import Evidence
from app.schemas.student import StudentCreate, StudentRead, StudentDetailRead

router = APIRouter(prefix="/students", tags=["Students"])


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
