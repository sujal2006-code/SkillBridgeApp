import os
import sys

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.student import Student
from app.models.skill import StudentSkill, Skill
from app.models.evidence import Evidence
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.models.match import Match
from app.models.internship import Internship

db = SessionLocal()
try:
    for s in db.query(Student).all():
        print(f"=== Student {s.id}: {s.name} ({s.email}), {s.university}, {s.graduation_year} ===")
        print("  Skills:")
        for ss in s.skills:
            print(f"    - {ss.skill.name if ss.skill else ss.skill_id}: {ss.proficiency_level} ({ss.verification_status})")
        print(f"  Evidence ({len(s.evidence)}):")
        for ev in s.evidence:
            skills_names = [sk.name for sk in ev.skills] if ev.skills else ([ev.skill.name] if ev.skill else [])
            print(f"    - [{ev.verification_status}] {ev.title} ({ev.evidence_type}) - Skills: {skills_names}, Issuer: {ev.issuer}")
finally:
    db.close()
