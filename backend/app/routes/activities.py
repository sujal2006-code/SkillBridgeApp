from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityRead

router = APIRouter(prefix="/activities", tags=["Activities & Notifications"])


@router.get("", response_model=List[ActivityRead], summary="List activity log entries")
def list_activities(
    student_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[ActivityRead]:
    """Retrieve persistent activity and notification log entries."""
    query = db.query(Activity)
    if student_id is not None:
        query = query.filter((Activity.student_id == student_id) | (Activity.student_id.is_(None)))
    
    return query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=ActivityRead, status_code=status.HTTP_201_CREATED, summary="Create an activity log entry")
def create_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
) -> ActivityRead:
    """Record a persistent user or system activity."""
    activity = Activity(**activity_in.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.patch("/{activity_id}/read", response_model=ActivityRead, summary="Mark activity as read")
def mark_activity_read(
    activity_id: int,
    db: Session = Depends(get_db),
) -> ActivityRead:
    """Mark a notification activity as read."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity item with ID {activity_id} not found.",
        )
    activity.is_read = True
    db.commit()
    db.refresh(activity)
    return activity
