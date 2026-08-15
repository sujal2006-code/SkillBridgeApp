from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database.session import get_db
from app.models.team import Team, TeamMember, TeamSkillRequirement
from app.models.student import Student
from app.models.skill import Skill
from app.models.activity import Activity
from app.schemas.team import (
    TeamCreate,
    TeamRead,
    TeamMemberCreate,
    TeamMemberRead,
    TeamCandidateRecommendation,
)
from app.services.team_matching import TeamMatchingService

router = APIRouter(prefix="/teams", tags=["Team Builder"])


def _map_team_to_schema(team: Team) -> TeamRead:
    """Helper to convert Team model to TeamRead schema with resolved names."""
    creator_name = team.creator.name if team.creator else None
    
    mapped_members = []
    for m in team.members:
        member_name = m.student.name if m.student else None
        mapped_members.append(
            TeamMemberRead(
                id=m.id,
                team_id=m.team_id,
                student_id=m.student_id,
                role=m.role,
                status=m.status,
                joined_at=m.joined_at,
                created_at=m.created_at,
                student_name=member_name,
            )
        )

    mapped_requirements = []
    for req in team.required_skills:
        skill_name = req.skill.name if req.skill else f"Skill #{req.skill_id}"
        mapped_requirements.append(
            {
                "id": req.id,
                "team_id": req.team_id,
                "skill_id": req.skill_id,
                "minimum_proficiency": req.minimum_proficiency,
                "required": req.required,
                "skill_name": skill_name,
            }
        )

    return TeamRead(
        id=team.id,
        name=team.name,
        description=team.description,
        creator_id=team.creator_id,
        creator_name=creator_name,
        created_at=team.created_at,
        members=mapped_members,
        required_skills=mapped_requirements,
    )


@router.get("", response_model=List[TeamRead], summary="List all teams")
def list_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[TeamRead]:
    """Retrieve all project teams."""
    teams = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            joinedload(Team.members).joinedload(TeamMember.student),
            joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
        )
        .order_by(Team.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_map_team_to_schema(t) for t in teams]


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED, summary="Create a new team")
def create_team(team_in: TeamCreate, db: Session = Depends(get_db)) -> TeamRead:
    """Create a new project team with initial skill requirements."""
    # Verify creator student exists
    creator = db.query(Student).filter(Student.id == team_in.creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student creator with ID {team_in.creator_id} not found.",
        )

    # 1. Create team record
    team = Team(
        name=team_in.name,
        description=team_in.description,
        creator_id=team_in.creator_id,
    )
    db.add(team)
    db.flush()

    # 2. Add creator as first team member (Lead/Owner)
    creator_member = TeamMember(
        team_id=team.id,
        student_id=team_in.creator_id,
        role="Team Owner & Lead",
        status="joined",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(creator_member)

    # 3. Add skill requirements if provided
    if team_in.required_skills:
        for req in team_in.required_skills:
            db.add(
                TeamSkillRequirement(
                    team_id=team.id,
                    skill_id=req.skill_id,
                    minimum_proficiency=req.minimum_proficiency,
                    required=req.required,
                )
            )
    elif team_in.required_skill_ids:
        for skill_id in team_in.required_skill_ids:
            db.add(
                TeamSkillRequirement(
                    team_id=team.id,
                    skill_id=skill_id,
                    minimum_proficiency="Intermediate",
                    required=True,
                )
            )

    # 4. Create persistent activity log
    activity = Activity(
        student_id=team_in.creator_id,
        activity_type="team",
        title=f"Created team \"{team.name}\"",
        description=f"Formed project team \"{team.name}\" to match multidisciplinary competencies.",
        icon="groups",
        related_entity_type="team",
        related_entity_id=team.id,
    )
    db.add(activity)

    db.commit()
    db.refresh(team)

    # Reload with relationships
    full_team = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            joinedload(Team.members).joinedload(TeamMember.student),
            joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
        )
        .filter(Team.id == team.id)
        .first()
    )
    return _map_team_to_schema(full_team)


@router.get("/{team_id}", response_model=TeamRead, summary="Get single team details")
def get_team(team_id: int, db: Session = Depends(get_db)) -> TeamRead:
    """Retrieve details for a single team."""
    team = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            joinedload(Team.members).joinedload(TeamMember.student),
            joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
        )
        .filter(Team.id == team_id)
        .first()
    )
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )
    return _map_team_to_schema(team)


@router.post("/{team_id}/members", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED, summary="Add or invite candidate to team")
def add_team_member(
    team_id: int,
    member_in: TeamMemberCreate,
    db: Session = Depends(get_db),
) -> TeamMemberRead:
    """Invite or add a student member to a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )

    student = db.query(Student).filter(Student.id == member_in.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {member_in.student_id} not found.",
        )

    # Check if student is already in team
    existing_member = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.student_id == member_in.student_id)
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student {student.name} is already a member or invited to this team.",
        )

    member = TeamMember(
        team_id=team_id,
        student_id=member_in.student_id,
        role=member_in.role,
        status=member_in.status,
        joined_at=datetime.now(timezone.utc) if member_in.status == "joined" else None,
    )
    db.add(member)

    # Create persistent activity log
    activity = Activity(
        student_id=team.creator_id,
        activity_type="team",
        title=f"Invited {student.name} to {team.name}",
        description=f"Sent team invitation for role {member_in.role}.",
        icon="person_add",
        related_entity_type="team",
        related_entity_id=team_id,
    )
    db.add(activity)

    db.commit()
    db.refresh(member)

    return TeamMemberRead(
        id=member.id,
        team_id=member.team_id,
        student_id=member.student_id,
        role=member.role,
        status=member.status,
        joined_at=member.joined_at,
        created_at=member.created_at,
        student_name=student.name,
    )


@router.get("/{team_id}/candidates", response_model=List[TeamCandidateRecommendation], summary="Get explainable candidate recommendations for team")
def get_team_candidates(team_id: int, db: Session = Depends(get_db)) -> List[TeamCandidateRecommendation]:
    """Retrieve explainable candidate recommendations from DB based on verified skill complementarity."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )

    return TeamMatchingService.get_candidate_recommendations_for_team(db, team_id)
