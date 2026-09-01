import os
import sys

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence, evidence_skills
from app.models.internship import Internship, InternshipSkill
from app.models.match import Match
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.models.activity import Activity
from app.models.professional_role import StudentProfessionalProfile

def clean_database():
    print("=" * 80)
    print("SKILLBRIDGE DATABASE CLEANUP: REMOVING OLD PERSONAL/TEST DATA")
    print("=" * 80)

    db = SessionLocal()

    # 1. Names/emails of old test/personal accounts to delete
    forbidden_names = [
        "sujal sahu",
        "somadutta sahu",
        "shiva mishra",
        "alex rivera",
    ]

    all_students = db.query(Student).all()
    students_to_delete = []

    for s in all_students:
        name_lower = (s.name or "").strip().lower()
        email_lower = (s.email or "").strip().lower()

        is_forbidden = any(f in name_lower for f in forbidden_names) or any(f.replace(" ", ".") in email_lower for f in forbidden_names)
        is_test_account = "student_1788" in name_lower or "student.1788" in email_lower or "kavya verma" in name_lower

        if is_forbidden or is_test_account:
            students_to_delete.append(s)

    del_ids = [s.id for s in students_to_delete]
    print(f"Found {len(students_to_delete)} test/personal student records to delete: {[(s.id, s.name, s.email) for s in students_to_delete]}")

    if del_ids:
        # Delete activities for these students
        del_acts = db.query(Activity).filter(Activity.student_id.in_(del_ids)).delete(synchronize_session=False)
        print(f"Deleted {del_acts} activities for test students")

        # Delete student professional profiles
        del_profs = db.query(StudentProfessionalProfile).filter(StudentProfessionalProfile.student_id.in_(del_ids)).delete(synchronize_session=False)
        print(f"Deleted {del_profs} professional profiles for test students")

        # Delete student skills
        del_skills = db.query(StudentSkill).filter(StudentSkill.student_id.in_(del_ids)).delete(synchronize_session=False)
        print(f"Deleted {del_skills} student skills for test students")

        # Delete evidence and evidence associations
        student_evs = db.query(Evidence).filter(Evidence.student_id.in_(del_ids)).all()
        for ev in student_evs:
            ev.skills = []
        db.flush()
        del_evs = db.query(Evidence).filter(Evidence.student_id.in_(del_ids)).delete(synchronize_session=False)
        print(f"Deleted {del_evs} evidence items for test students")

        # Delete internships matches
        del_matches = db.query(Match).filter(Match.student_id.in_(del_ids)).delete(synchronize_session=False)
        print(f"Deleted {del_matches} internship matches for test students")

        # Delete team invitations where sender or recipient is in del_ids
        del_invs = db.query(TeamInvitation).filter(
            (TeamInvitation.sender_id.in_(del_ids)) | (TeamInvitation.recipient_id.in_(del_ids))
        ).delete(synchronize_session=False)
        print(f"Deleted {del_invs} team invitations for test students")

        # Delete team members where student_id in del_ids
        del_members = db.query(TeamMember).filter(TeamMember.student_id.in_(del_ids)).delete(synchronize_session=False)
        print(f"Deleted {del_members} team memberships for test students")

        # Delete student records
        for s in students_to_delete:
            db.delete(s)
        db.commit()
        print(f"Successfully deleted {len(students_to_delete)} student records.")

    # 2. Delete ALL existing teams, team members, invitations, and requirements
    # So that the application starts with a clean 0-team state ("No team yet")
    print("\n--- Cleaning All Team Records for Fresh Initial State ---")
    db.query(TeamInvitation).delete(synchronize_session=False)
    db.query(TeamMember).delete(synchronize_session=False)
    db.query(TeamSkillRequirement).delete(synchronize_session=False)
    del_teams = db.query(Team).delete(synchronize_session=False)
    db.commit()
    print(f"Deleted all {del_teams} old team records, team members, and invitations.")

    # 3. Clean any lingering activities related to teams
    del_team_acts = db.query(Activity).filter(
        Activity.activity_type.in_(["team_created", "team_joined", "team_invitation"])
    ).delete(synchronize_session=False)
    db.commit()
    print(f"Deleted {del_team_acts} team-related activity notifications.")

    # 4. Verify remaining students
    remaining = db.query(Student).all()
    print(f"\nRemaining legitimate student accounts: {len(remaining)}")
    for r in remaining:
        print(f"  #{r.id}: {r.name} ({r.email}) - {r.university}")

    print("\n" + "=" * 80)
    print("DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    clean_database()
