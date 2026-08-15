from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.internship import Internship, InternshipSkill
from app.schemas.internship import InternshipCreate, InternshipRead

router = APIRouter(prefix="/internships", tags=["Internships"])


@router.post("", response_model=InternshipRead, status_code=status.HTTP_201_CREATED)
def create_internship(internship_in: InternshipCreate, db: Session = Depends(get_db)) -> Internship:
    """Create a new internship opportunity."""
    data = internship_in.model_dump(exclude={"skills_required"})
    internship = Internship(**data)
    db.add(internship)
    db.flush()

    if internship_in.skills_required:
        for sk in internship_in.skills_required:
            db.add(InternshipSkill(internship_id=internship.id, **sk.model_dump()))

    db.commit()
    db.refresh(internship)
    return internship


@router.get("", response_model=List[InternshipRead])
def list_internships(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)) -> List[Internship]:
    """Retrieve all internship opportunities with required skills."""
    return (
        db.query(Internship)
        .options(
            joinedload(Internship.internship_skills).joinedload(InternshipSkill.skill)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{internship_id}", response_model=InternshipRead)
def get_internship(internship_id: int, db: Session = Depends(get_db)) -> Internship:
    """Retrieve specific internship details."""
    internship = (
        db.query(Internship)
        .options(
            joinedload(Internship.internship_skills).joinedload(InternshipSkill.skill)
        )
        .filter(Internship.id == internship_id)
        .first()
    )
    if not internship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found.",
        )
    return internship
