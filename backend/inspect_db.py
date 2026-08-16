import os
import sys

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal
from app.models.student import Student
from app.models.otp import OTP
from app.models.skill import Skill
from app.models.internship import Internship
from app.models.team import Team

db = SessionLocal()
try:
    students = db.query(Student).all()
    print(f"Total Students: {len(students)}")
    for s in students:
        print(f" - ID: {s.id}, Name: '{s.name}', Email: '{s.email}'")

    otps = db.query(OTP).all()
    print(f"Total OTPs: {len(otps)}")
    for o in otps:
        print(f" - OTP ID: {o.id}, Email: '{o.email}', Purpose: '{o.purpose}', Used: {o.is_used}")

    print(f"Skills count: {db.query(Skill).count()}")
    print(f"Internships count: {db.query(Internship).count()}")
    print(f"Teams count: {db.query(Team).count()}")
finally:
    db.close()
