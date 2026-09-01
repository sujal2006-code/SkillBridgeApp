import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings

# SQLAlchemy declarative base for data models
Base = declarative_base()

# SQLAlchemy engine - PostgreSQL ready & SQLite local dev compatible
db_url = settings.sync_database_url

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        db_url,
        connect_args=connect_args,
    )
else:
    # Production PostgreSQL connection (Neon / Supabase / RDS / Serverless)
    # 1. Normalize postgres:// to postgresql://
    if db_url.startswith("postgres://"):
        db_url = "postgresql://" + db_url[len("postgres://"):]

    # 2. Serverless PostgreSQL engine configuration
    # NullPool prevents connection leaks and broken sockets across serverless invocations
    # connect_timeout 15s allows Neon computes to cold-start from sleep
    connect_args = {"connect_timeout": 15}
    if "sslmode" not in db_url:
        connect_args["sslmode"] = "require"

    engine = create_engine(
        db_url,
        poolclass=NullPool,
        connect_args=connect_args,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
