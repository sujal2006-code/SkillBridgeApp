from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLAlchemy declarative base for data models
Base = declarative_base()

# SQLAlchemy engine - PostgreSQL ready & SQLite local dev compatible
db_url = settings.sync_database_url
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine = create_engine(
        db_url,
        connect_args=connect_args,
    )
else:
    # Production PostgreSQL connection with serverless-friendly pooling & auto-reconnect
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 3},
        )
        # Test connection immediately with short timeout
        with engine.connect() as conn:
            pass
    except Exception as e:
        print(f"[WARN] Remote database connection failed ({e}). Falling back to local SQLite database.")
        engine = create_engine(
            "sqlite:///./skillbridge.db",
            connect_args={"check_same_thread": False},
        )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
