from typing import List, Optional, Dict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from app.database.session import get_db
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence
from app.models.activity import Activity
from app.models.professional_role import StudentProfessionalProfile
from app.schemas.team import (
    TeamCreate,
    TeamRead,
    TeamMemberCreate,
    TeamMemberRead,
    TeamSkillRequirementCreate,
    TeamSkillRequirementRead,
    TeamInvitationCreate,
    TeamInvitationRead,
    TeamCandidateRecommendation,
)
from app.services.team_matching import TeamMatchingService, DOMAIN_CATEGORIES, normalize_skill_name
from app.services.professional_role_service import ProfessionalRoleService
from app.core.security import get_current_student_id, get_optional_student_id

router = APIRouter(prefix="/teams", tags=["Team Builder"])

MAX_TEAM_MEMBERS = 6


def _map_team_to_schema(team: Team, db: Session) -> TeamRead:
    """Helper to convert Team model to rich TeamRead schema with members, gaps, and coverage."""
    creator_name = team.creator.name if team.creator else None
    project_name = team.project_name or team.description or "Multidisciplinary Project Platform"

    mapped_members: List[TeamMemberRead] = []
    joined_student_ids: List[int] = []

    for m in team.members:
        if m.status != "joined":
            continue
        member_student = m.student
        member_name = member_student.name if member_student else None
        
        prof_role = "Technical Contributor"
        prof_level = "Intermediate"
        domains: List[str] = []
        verified_skills: List[str] = []
        evidence_items: List[str] = []

        if member_student:
            if m.status == "joined":
                joined_student_ids.append(m.student_id)

            # Fetch member's professional profile
            prof = member_student.professional_profile
            if not prof:
                prof = db.query(StudentProfessionalProfile).filter(StudentProfessionalProfile.student_id == member_student.id).first()
            if prof:
                prof_role = prof.primary_role

            # Calculate verified skills and domain proficiencies
            for ss in member_student.skills:
                if ss.verification_status == "verified" and ss.skill:
                    verified_skills.append(ss.skill.name)
                    if ss.proficiency_level == "Advanced":
                        prof_level = "Advanced"

            # Domain breakdown
            domain_evals = ProfessionalRoleService.calculate_student_domain_proficiencies(member_student)
            domains = [d["domain"] for d in domain_evals if d["is_supported"]]

            # Evidence artifacts
            for ev in member_student.evidence:
                if ev.verification_status == "verified":
                    evidence_items.append(f"{ev.title} ({ev.evidence_type.title()})")

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
                professional_role=prof_role,
                proficiency=prof_level,
                domains=domains,
                verified_skills=verified_skills,
                evidence_items=evidence_items[:4],
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
    domain_coverage: Dict[str, bool] = {}

    for req in team.required_skills:
        skill_name = req.skill.name if req.skill else f"Skill #{req.skill_id}"
        req_domain = req.domain or TeamMatchingService.get_skill_domain(skill_name)
        is_covered = skill_name in covered_skills
        if not is_covered:
            missing_skills.append(skill_name)

        if req_domain:
            domain_coverage[req_domain] = domain_coverage.get(req_domain, False) or is_covered

        mapped_requirements.append(
            TeamSkillRequirementRead(
                id=req.id,
                team_id=req.team_id,
                skill_id=req.skill_id,
                skill_name=skill_name,
                domain=req_domain,
                minimum_proficiency=req.minimum_proficiency,
                required=req.required,
            )
        )

    # Map invitations
    mapped_invitations = []
    for inv in team.invitations:
        mapped_invitations.append(
            TeamInvitationRead(
                id=inv.id,
                team_id=inv.team_id,
                team_name=team.name,
                project_name=project_name,
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

    total_reqs = len(team.required_skills)
    coverage_pct = round((len(covered_skills) / max(1, total_reqs)) * 100.0, 1) if total_reqs > 0 else 100.0

    return TeamRead(
        id=team.id,
        name=team.name,
        project_name=project_name,
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
        team_coverage_percentage=min(100.0, coverage_pct),
        domain_coverage=domain_coverage,
    )


@router.get("", response_model=List[TeamRead], summary="List all teams")
def list_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[TeamRead]:
    """Retrieve all project teams with skill requirements and members."""
    teams = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills).joinedload(StudentSkill.skill),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.evidence),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.professional_profile),
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


@router.get("/my", response_model=List[TeamRead], summary="Get teams for authenticated student")
def get_my_teams(
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> List[TeamRead]:
    """Retrieve teams where the current student is either Team Leader (creator) or joined Member."""
    teams = (
        db.query(Team)
        .join(TeamMember, Team.id == TeamMember.team_id)
        .options(
            joinedload(Team.creator),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills).joinedload(StudentSkill.skill),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.evidence),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.professional_profile),
            selectinload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            selectinload(Team.invitations).joinedload(TeamInvitation.sender),
            selectinload(Team.invitations).joinedload(TeamInvitation.recipient),
        )
        .filter(
            (Team.creator_id == auth_student_id) |
            ((TeamMember.student_id == auth_student_id) & (TeamMember.status == "joined"))
        )
        .distinct()
        .order_by(Team.created_at.desc())
        .all()
    )
    return [_map_team_to_schema(t, db) for t in teams]


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED, summary="Create a new team")
def create_team(
    team_in: TeamCreate,
    auth_student_id: Optional[int] = Depends(get_optional_student_id),
    db: Session = Depends(get_db),
) -> TeamRead:
    """Create a new project team with required capabilities and creator as Team Leader."""
    effective_creator_id = auth_student_id if auth_student_id is not None else (team_in.creator_id or 1)
    creator = db.query(Student).filter(Student.id == effective_creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student creator with ID {effective_creator_id} not found.",
        )

    # 1. Create team record
    team = Team(
        name=team_in.name.strip(),
        project_name=team_in.project_name.strip() if team_in.project_name else team_in.name.strip(),
        description=team_in.description.strip() if team_in.description else None,
        creator_id=effective_creator_id,
    )
    db.add(team)
    db.flush()

    # 2. Add creator as Team Leader
    creator_member = TeamMember(
        team_id=team.id,
        student_id=effective_creator_id,
        role="Team Leader",
        status="joined",
        joined_at=datetime.now(timezone.utc),
    )
    db.add(creator_member)

    # 3. Add skill requirements from explicit items, IDs, or domain keywords
    added_skill_ids = set()

    if team_in.required_skills:
        for req in team_in.required_skills:
            sk_id = req.skill_id
            if not sk_id and req.skill_name:
                sk = db.query(Skill).filter(Skill.name.ilike(req.skill_name.strip())).first()
                if not sk:
                    sk = Skill(name=req.skill_name.strip(), category=req.domain or "Technical", description=f"Skill in {req.skill_name}")
                    db.add(sk)
                    db.flush()
                sk_id = sk.id
            
            if sk_id and sk_id not in added_skill_ids:
                added_skill_ids.add(sk_id)
                db.add(
                    TeamSkillRequirement(
                        team_id=team.id,
                        skill_id=sk_id,
                        domain=req.domain,
                        minimum_proficiency=req.minimum_proficiency or "Intermediate",
                        required=req.required,
                    )
                )
    elif team_in.required_skill_ids:
        for skill_id in team_in.required_skill_ids:
            if skill_id not in added_skill_ids:
                added_skill_ids.add(skill_id)
                db.add(
                    TeamSkillRequirement(
                        team_id=team.id,
                        skill_id=skill_id,
                        minimum_proficiency="Intermediate",
                        required=True,
                    )
                )

    # 4. If required_domains passed (e.g. ["Frontend & UI", "Backend Development", "ML & AI"])
    if team_in.required_domains:
        domain_skill_defaults = {
            "Frontend & UI": "React",
            "Frontend": "React",
            "Backend Development": "Python",
            "Backend": "Python",
            "Data Systems / Database": "SQL",
            "Data Systems": "SQL",
            "Database": "SQL",
            "ML & AI": "Machine Learning",
            "AI/ML": "Machine Learning",
            "UI/UX": "UI/UX",
            "DevOps": "Docker",
            "DevOps & Cloud": "Docker",
        }
        for d_name in team_in.required_domains:
            def_skill_name = domain_skill_defaults.get(d_name, d_name)
            sk = db.query(Skill).filter(Skill.name.ilike(def_skill_name)).first()
            if not sk:
                sk = Skill(name=def_skill_name, category=d_name, description=f"Required competency for {d_name}")
                db.add(sk)
                db.flush()
            if sk.id not in added_skill_ids:
                added_skill_ids.add(sk.id)
                db.add(
                    TeamSkillRequirement(
                        team_id=team.id,
                        skill_id=sk.id,
                        domain=d_name,
                        minimum_proficiency="Intermediate",
                        required=True,
                    )
                )

    # 5. Persistent activity log
    activity = Activity(
        student_id=effective_creator_id,
        activity_type="team",
        title=f"Created team \"{team.name}\"",
        description=f"Formed project team \"{team.name}\" for project \"{team.project_name}\".",
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
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills).joinedload(StudentSkill.skill),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.evidence),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.professional_profile),
            selectinload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            selectinload(Team.invitations),
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
                project_name=inv.team.project_name if inv.team else None,
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

    # 5. Create persistent invitation
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
    sender_name = sender.name if sender else "Team Leader"
    recipient_activity = Activity(
        student_id=inv_in.recipient_id,
        activity_type="team_invitation",
        title=f"Team Invitation: {team.name}",
        description=f"{sender_name} invited you to join \"{team.name}\" ({team.project_name or 'Project'}) as {inv_in.role}.",
        icon="group_add",
        related_entity_type="team_invitation",
        related_entity_id=invitation.id,
    )
    db.add(recipient_activity)

    db.commit()
    db.refresh(invitation)

    return TeamInvitationRead(
        id=invitation.id,
        team_id=invitation.team_id,
        team_name=team.name,
        project_name=team.project_name,
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
        project_name=team.project_name,
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
        db.delete(member)

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
        project_name=invitation.team.project_name if invitation.team else None,
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
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills).joinedload(StudentSkill.skill),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.evidence),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.professional_profile),
            selectinload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            selectinload(Team.invitations),
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


@router.put("/{team_id}/requirements", response_model=TeamRead, summary="Update team required capabilities")
def update_team_requirements(
    team_id: int,
    requirements: List[TeamSkillRequirementCreate],
    auth_student_id: int = Depends(get_current_student_id),
    db: Session = Depends(get_db),
) -> TeamRead:
    """Update team skill requirements (team leader only)."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )
    if team.creator_id != auth_student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only the Team Leader can update team requirements.",
        )

    # Delete existing requirements
    db.query(TeamSkillRequirement).filter(TeamSkillRequirement.team_id == team_id).delete()

    added_skill_ids = set()
    for req in requirements:
        sk_id = req.skill_id
        if not sk_id and req.skill_name:
            sk = db.query(Skill).filter(Skill.name.ilike(req.skill_name.strip())).first()
            if not sk:
                sk = Skill(name=req.skill_name.strip(), category=req.domain or "Technical", description=f"Skill in {req.skill_name}")
                db.add(sk)
                db.flush()
            sk_id = sk.id
        
        if sk_id and sk_id not in added_skill_ids:
            added_skill_ids.add(sk_id)
            db.add(
                TeamSkillRequirement(
                    team_id=team.id,
                    skill_id=sk_id,
                    domain=req.domain,
                    minimum_proficiency=req.minimum_proficiency or "Intermediate",
                    required=req.required,
                )
            )

    db.commit()
    db.refresh(team)

    full_team = (
        db.query(Team)
        .options(
            joinedload(Team.creator),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.skills).joinedload(StudentSkill.skill),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.evidence),
            selectinload(Team.members).joinedload(TeamMember.student).joinedload(Student.professional_profile),
            selectinload(Team.required_skills).joinedload(TeamSkillRequirement.skill),
            selectinload(Team.invitations),
        )
        .filter(Team.id == team.id)
        .first()
    )
    return _map_team_to_schema(full_team, db)


@router.get("/{team_id}/candidates", response_model=List[TeamCandidateRecommendation], summary="Get explainable candidate recommendations for team")
def get_team_candidates(
    team_id: int,
    target_role: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[TeamCandidateRecommendation]:
    """
    Retrieve explainable candidate recommendations based on team skill gaps and complementarity.
    Supports role-specific recalculation via target_role or domain parameter.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with ID {team_id} not found.",
        )

    return TeamMatchingService.get_candidate_recommendations_for_team(
        db=db,
        team_id=team_id,
        target_role=target_role,
        target_domain=domain,
    )
