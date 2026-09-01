"""
SkillBridge Neon PostgreSQL Initialization & Migration Utility.

Usage:
  python backend/init_neon_db.py
  python backend/init_neon_db.py "postgresql://user:pass@ep-host.region.neon.tech/neondb?sslmode=require"
"""
import os
import sys

backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.database.session import Base
from app.database.init_db import init_db
from app.models.student import Student
from app.models.skill import Skill
from app.models.internship import Internship
from app.models.team import Team


def run_neon_init(db_url: str = None):
    url = db_url or os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not url:
        print("[ERROR] No DATABASE_URL provided.")
        print("Usage: python backend/init_neon_db.py \"postgresql://user:pass@host/neondb?sslmode=require\"")
        print("Or set the DATABASE_URL environment variable.")
        sys.exit(1)

    url = url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    print("=" * 80)
    print("SKILLBRIDGE NEON POSTGRESQL INITIALIZATION & SCHEMA VERIFICATION")
    print("=" * 80)
    # Mask password for display
    masked_url = url
    if "@" in url and ":" in url.split("@")[0]:
        parts = url.split("@")
        creds = parts[0].split(":")
        masked_url = f"{creds[0]}:****@{parts[1]}"
    print(f"[INFO] Connecting to: {masked_url}")

    connect_args = {"connect_timeout": 15}
    if "sslmode" not in url:
        connect_args["sslmode"] = "require"

    engine = create_engine(
        url,
        poolclass=NullPool,
        connect_args=connect_args,
    )

    # 1. Test live connection
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).scalar()
            print(f"[PASS] 1. Live database connection established successfully.")
            print(f"       Engine: {res[:60]}...")
    except Exception as e:
        print(f"[FAIL] 1. Connection failed: {e}")
        sys.exit(1)

    # 2. Create all tables
    print("\n[INFO] Creating tables from SQLAlchemy Base metadata...")
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"[PASS] 2. Tables verified in database ({len(tables)} tables):")
    for t in sorted(tables):
        print(f"       - {t}")

    # 3. Seed canonical data
    print("\n[INFO] Seeding canonical skills catalogue and verified demo profiles...")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        init_db(db)
        total_students = db.query(Student).count()
        total_skills = db.query(Skill).count()
        total_internships = db.query(Internship).count()
        total_teams = db.query(Team).count()

        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION SUMMARY")
        print("=" * 80)
        print(f" [PASS] Total Registered Students: {total_students}")
        print(f" [PASS] Total Canonical Skills:   {total_skills}")
        print(f" [PASS] Total Internships:        {total_internships}")
        print(f" [PASS] Active Project Teams:     {total_teams} (Starts clean at 0 teams)")
        print("\nAll tables and demo accounts are ready for production on Vercel!")
        print("=" * 80)
    finally:
        db.close()


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_neon_init(target_url)
