from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from app.database.session import get_db
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.activity import Activity
from app.schemas.team import (
    TeamCreate,
    TeamRead,
    TeamMemberCreate,
    TeamMemberRead,
    TeamInvitationCreate,
    TeamInvitationRead,
    TeamCandidateRecommendation,
)
from app.services.team_matching import TeamMatchingService
from app.core.security import get_current_student_id, get_optional_student_id

router = APIRouter(prefix="/teams", tags=["Team Builder"])

MAX_TEAM_MEMBERS = 6


def _map_team_to_schema(team: Team, db: Session) -> TeamRead:
    """Helper to convert Team model to rich TeamRead schema with members, gaps, and coverage."""
    creator_name = team.creator.name if team.creator else None
    
    mapped_members = []
    joined_student_ids = []
    for m in team.members:
        member_name = m.student.name if m.student else None
        if m.status == "joined":
            joined_student_ids.append(m.student_id)
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

    # Compute skills covered by joined members
    covered_skills = set()
    if joined_student_ids:
        joined_student_skills = (
            db.query(StudentSkill)
            .options(joinedload(StudentSkill.skill))
            .filter(
                StudentSkill.student_id.in_(joined_student_ids),
                StudentSkill.verification_status == "verified",
            )
            .all()
        )
        for ss in joined_student_skills:
            if ss.skill:
                covered_skills.add(ss.skill.name)

    mapped_requirements = []
    missing_skills = []
    for req in team.required_skills:
        skill_name = req.skill.name if req.skill else f"Skill #{req.skill_id}"
        if skill_name not in covered_skills:
            missing_skills.append(skill_name)
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

    # Map invitations
    mapped_invitations = []
    for inv in team.invitations:
        mapped_invitations.append(
            TeamInvitationRead(
                id=inv.id,
                team_id=inv.team_id,
                team_name=team.name,
                sender_id=inv.sender_id,
                sender_name=inv.sender.name if inv.sender else None,
                recipient_id=inv.recipient_id,
                recipient_name=inv.recipient.name if inv.recipient else None,
                role=inv.role,
                message=inv.message,
                status=inv.status,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
            )
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
        invitations=mapped_invitations,
        total_members_count=len([m for m in team.members if m.status == "joined"]),
        skills_covered=sorted(list(covered_skills)),
        skills_missing=missing_skills,
    )


@router.get("", response_model=List[TeamRead], summary="List all teams")
def list_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[TeamRead]:
    """Retrieve all project teams with skill requirements and members."""
    teams = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            selectinload(Team.members).joinedload(TeamMember.student),
            selectinload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            selectinload(Team.invitations).joinedload(TeamInvitation.sender),
            selectinload(Team.invitations).joinedload(TeamInvitation.recipient),
        )
        .order_by(Team.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_map_team_to_schema(t, db) for t in teams]


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED, summary="Create a new team")
def create_team(
    team_in: TeamCreate,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> TeamRead:
    """Create a new project team with initial skill requirements and creator as lead."""
    effective_creator_id = auth_student_id if auth_student_id is not None else team_in.creator_id
    creator = db.query(Student).filter(Student.id == effective_creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student creator with ID {effective_creator_id} not found.",
        )

    # 1. Create team record
    team = Team(
        name=team_in.name,
        description=team_in.description,
        creator_id=effective_creator_id,
    )
    db.add(team)
    db.flush()

    # 2. Add creator as first team member (Lead/Owner)
    creator_member = TeamMember(
        team_id=team.id,
        student_id=effective_creator_id,
        role="Team Owner & Lead",
        status="joined",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(creator_member)

    # 3. Add skill requirements
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
        student_id=effective_creator_id,
        activity_type="team",
        title=f"Created team \"{team.name}\"",
        description=f"Formed project team \"{team.name}\" for collaborative problem solving.",
        icon="groups",
        related_entity_type="team",
        related_entity_id=team.id,
    )
    db.add(activity)

    db.commit()
    db.refresh(team)

    full_team = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            joinedload(Team.members).joinedload(TeamMember.student),
            joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            joinedload(Team.invitations),
        )
        .filter(Team.id == team.id)
        .first()
    )
    return _map_team_to_schema(full_team, db)


@router.get("/invitations/pending", response_model=List[TeamInvitationRead], summary="Get pending invitations for current student")
def get_pending_invitations(
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> List[TeamInvitationRead]:
    """Retrieve all pending team invitations addressed to the authenticated student."""
    invitations = (
        db.query(TeamInvitation)
        .options(
            joinedload(TeamInvitation.team),
            joinedload(TeamInvitation.sender),
            joinedload(TeamInvitation.recipient),
        )
        .filter(
            TeamInvitation.recipient_id == auth_student_id,
            TeamInvitation.status == "PENDING",
        )
        .order_by(TeamInvitation.created_at.desc())
        .all()
    )

    results = []
    for inv in invitations:
        # Determine skills recipient contributes to team
        recipient_skills = (
            db.query(StudentSkill)
            .options(joinedload(StudentSkill.skill))
            .filter(
                StudentSkill.student_id == auth_student_id,
                StudentSkill.verification_status == "verified",
            )
            .all()
        )
        contributed = [ss.skill.name for ss in recipient_skills if ss.skill]

        results.append(
            TeamInvitationRead(
                id=inv.id,
                team_id=inv.team_id,
                team_name=inv.team.name if inv.team else None,
                sender_id=inv.sender_id,
                sender_name=inv.sender.name if inv.sender else None,
                recipient_id=inv.recipient_id,
                recipient_name=inv.recipient.name if inv.recipient else None,
                role=inv.role,
                message=inv.message,
                status=inv.status,
                created_at=inv.created_at,
                updated_at=inv.updated_at,
                contributed_skills=contributed[:4],
            )
        )
    return results


@router.post("/{team_id}/invitations", response_model=TeamInvitationRead, status_code=status.HTTP_201_CREATED, summary="Send persistent team invitation")
def create_team_invitation(
    team_id: int,
    inv_in: TeamInvitationCreate,
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> TeamInvitationRead:
    """Send a persistent team invitation with duplicate and capacity validation."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )

    # 1. Prevent self-invitation
    if auth_student_id == inv_in.recipient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot invite yourself to your own team.",
        )

    # 2. Check team capacity
    current_members_count = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.status == "joined").count()
    if current_members_count >= MAX_TEAM_MEMBERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team has reached the maximum capacity of {MAX_TEAM_MEMBERS} members.",
        )

    # 3. Check existing membership
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.student_id == inv_in.recipient_id,
        TeamMember.status == "joined",
    ).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already an active member of this team.",
        )

    # 4. Check active pending invitation
    existing_inv = db.query(TeamInvitation).filter(
        TeamInvitation.team_id == team_id,
        TeamInvitation.recipient_id == inv_in.recipient_id,
        TeamInvitation.status == "PENDING",
    ).first()
    if existing_inv:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending invitation has already been sent to this student.",
        )

    recipient = db.query(Student).filter(Student.id == inv_in.recipient_id).first()
    sender = db.query(Student).filter(Student.id == auth_student_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipient student with ID {inv_in.recipient_id} not found.",
        )

    # 5. Create TeamInvitation record
    invitation = TeamInvitation(
        team_id=team_id,
        sender_id=auth_student_id,
        recipient_id=inv_in.recipient_id,
        role=inv_in.role,
        message=inv_in.message,
        status="PENDING",
    )
    db.add(invitation)
    db.flush()

    # 6. Add/Update TeamMember entry with 'invited' status for tracking
    tm = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.student_id == inv_in.recipient_id).first()
    if not tm:
        tm = TeamMember(
            team_id=team_id,
            student_id=inv_in.recipient_id,
            role=inv_in.role,
            status="invited",
        )
        db.add(tm)
    else:
        tm.status = "invited"
        tm.role = inv_in.role

    # 7. Create persistent recipient notification
    sender_name = sender.name if sender else "A teammate"
    recipient_activity = Activity(
        student_id=inv_in.recipient_id,
        activity_type="team_invitation",
        title=f"Team Invitation: {team.name}",
        description=f"{sender_name} invited you to join \"{team.name}\" as {inv_in.role}.",
        icon="group_add",
        related_entity_type="team_invitation",
        related_entity_id=invitation.id,
    )
    db.add(recipient_activity)

    # 8. Create sender activity log
    sender_activity = Activity(
        student_id=auth_student_id,
        activity_type="team",
        title=f"Sent invitation to {recipient.name}",
        description=f"Invited {recipient.name} to join team \"{team.name}\".",
        icon="send",
        related_entity_type="team",
        related_entity_id=team_id,
    )
    db.add(sender_activity)

    db.commit()
    db.refresh(invitation)

    return TeamInvitationRead(
        id=invitation.id,
        team_id=invitation.team_id,
        team_name=team.name,
        sender_id=invitation.sender_id,
        sender_name=sender.name if sender else None,
        recipient_id=invitation.recipient_id,
        recipient_name=recipient.name if recipient else None,
        role=invitation.role,
        message=invitation.message,
        status=invitation.status,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
    )


@router.post("/invitations/{invitation_id}/accept", response_model=TeamInvitationRead, summary="Accept team invitation")
def accept_team_invitation(
    invitation_id: int,
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> TeamInvitationRead:
    """Accept team invitation, add student to team, and update team skill coverage."""
    invitation = (
        db.query(TeamInvitation)
        .options(joinedload(TeamInvitation.team), joinedload(TeamInvitation.sender), joinedload(TeamInvitation.recipient))
        .filter(TeamInvitation.id == invitation_id)
        .first()
    )
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found.",
        )

    if invitation.recipient_id != auth_student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot respond to an invitation sent to another student.",
        )

    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is already {invitation.status.lower()}.",
        )

    # Verify team capacity
    team = db.query(Team).filter(Team.id == invitation.team_id).first()
    current_members_count = db.query(TeamMember).filter(TeamMember.team_id == invitation.team_id, TeamMember.status == "joined").count()
    if current_members_count >= MAX_TEAM_MEMBERS:
        invitation.status = "CANCELLED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team has reached its maximum capacity. Invitation could not be accepted.",
        )

    # 1. Update Invitation Status
    invitation.status = "ACCEPTED"
    invitation.updated_at = datetime.now(timezone.utc)

    # 2. Add/Update TeamMember
    member = db.query(TeamMember).filter(
        TeamMember.team_id == invitation.team_id,
        TeamMember.student_id == auth_student_id,
    ).first()
    if not member:
        member = TeamMember(
            team_id=invitation.team_id,
            student_id=auth_student_id,
            role=invitation.role,
            status="joined",
            joined_at=datetime.now(timezone.utc),
        )
        db.add(member)
    else:
        member.status = "joined"
        member.role = invitation.role
        member.joined_at = datetime.now(timezone.utc)

    # 3. Mark invitation notification as read
    notif = db.query(Activity).filter(
        Activity.student_id == auth_student_id,
        Activity.related_entity_type == "team_invitation",
        Activity.related_entity_id == invitation_id,
    ).first()
    if notif:
        notif.is_read = True

    # 4. Notify Team Creator
    creator_activity = Activity(
        student_id=team.creator_id,
        activity_type="team",
        title=f"{invitation.recipient.name} joined {team.name}",
        description=f"{invitation.recipient.name} accepted your team invitation as {invitation.role}.",
        icon="how_to_reg",
        related_entity_type="team",
        related_entity_id=team.id,
    )
    db.add(creator_activity)

    db.commit()
    db.refresh(invitation)

    return TeamInvitationRead(
        id=invitation.id,
        team_id=invitation.team_id,
        team_name=team.name,
        sender_id=invitation.sender_id,
        sender_name=invitation.sender.name if invitation.sender else None,
        recipient_id=invitation.recipient_id,
        recipient_name=invitation.recipient.name if invitation.recipient else None,
        role=invitation.role,
        message=invitation.message,
        status=invitation.status,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
    )


@router.post("/invitations/{invitation_id}/reject", response_model=TeamInvitationRead, summary="Reject team invitation")
def reject_team_invitation(
    invitation_id: int,
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> TeamInvitationRead:
    """Reject team invitation and update notification status."""
    invitation = (
        db.query(TeamInvitation)
        .options(joinedload(TeamInvitation.team), joinedload(TeamInvitation.sender), joinedload(TeamInvitation.recipient))
        .filter(TeamInvitation.id == invitation_id)
        .first()
    )
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found.",
        )

    if invitation.recipient_id != auth_student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot reject an invitation addressed to another student.",
        )

    if invitation.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation is already {invitation.status.lower()}.",
        )

    invitation.status = "REJECTED"
    invitation.updated_at = datetime.now(timezone.utc)

    # Update member status if exists
    member = db.query(TeamMember).filter(
        TeamMember.team_id == invitation.team_id,
        TeamMember.student_id == auth_student_id,
    ).first()
    if member:
        member.status = "declined"

    # Mark notification as read
    notif = db.query(Activity).filter(
        Activity.student_id == auth_student_id,
        Activity.related_entity_type == "team_invitation",
        Activity.related_entity_id == invitation_id,
    ).first()
    if notif:
        notif.is_read = True

    db.commit()
    db.refresh(invitation)

    return TeamInvitationRead(
        id=invitation.id,
        team_id=invitation.team_id,
        team_name=invitation.team.name if invitation.team else None,
        sender_id=invitation.sender_id,
        sender_name=invitation.sender.name if invitation.sender else None,
        recipient_id=invitation.recipient_id,
        recipient_name=invitation.recipient.name if invitation.recipient else None,
        role=invitation.role,
        message=invitation.message,
        status=invitation.status,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
    )


@router.get("/{team_id}", response_model=TeamRead, summary="Get single team details")
def get_team(team_id: int, db: Session = Depends(get_db)) -> TeamRead:
    """Retrieve details for a single team."""
    team = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            joinedload(Team.members).joinedload(TeamMember.student),
            joinedload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            joinedload(Team.invitations),
        )
        .filter(Team.id == team_id)
        .first()
    )
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )
    return _map_team_to_schema(team, db)


@router.post("/{team_id}/members", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED, summary="Add candidate directly to team")
def add_team_member(
    team_id: int,
    member_in: TeamMemberCreate,
    db: Session = Depends(get_db),
) -> TeamMemberRead:
    """Add a student directly as member to a team."""
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

    existing_member = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.student_id == member_in.student_id)
        .first()
    )
    if existing_member:
        existing_member.status = member_in.status
        existing_member.role = member_in.role
        existing_member.joined_at = datetime.now(timezone.utc) if member_in.status == "joined" else existing_member.joined_at
        db.commit()
        db.refresh(existing_member)
        member = existing_member
    else:
        member = TeamMember(
            team_id=team_id,
            student_id=member_in.student_id,
            role=member_in.role,
            status=member_in.status,
            joined_at=datetime.now(timezone.utc) if member_in.status == "joined" else None,
        )
        db.add(member)
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
    """Retrieve explainable candidate recommendations based on team skill gaps and complementarity."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )

    return TeamMatchingService.get_candidate_recommendations_for_team(db, team_id)
