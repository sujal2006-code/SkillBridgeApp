from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillRead

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
def create_skill(skill_in: SkillCreate, db: Session = Depends(get_db)) -> Skill:
    """Create a new skill definition."""
    existing = db.query(Skill).filter(Skill.name.ilike(skill_in.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill '{skill_in.name}' already exists.",
        )
    skill = Skill(**skill_in.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.get("", response_model=List[SkillRead])
def list_skills(category: str = None, db: Session = Depends(get_db)) -> List[Skill]:
    """Retrieve all available skills with optional category filter."""
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return query.order_by(Skill.name).all()
