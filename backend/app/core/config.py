import os
import shutil
from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillBridge API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # CORS settings
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, set)):
            return [str(i) for i in v]
        return []

    # Database settings (PostgreSQL ready with SQLite local development default)
    DATABASE_URL: Union[str, None] = None
    POSTGRES_URL: Union[str, None] = None
    POSTGRES_PRISMA_URL: Union[str, None] = None
    POSTGRES_URL_NON_POOLING: Union[str, None] = None
    POSTGRES_SERVER: Union[str, None] = None
    POSTGRES_HOST: Union[str, None] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: Union[str, None] = None
    POSTGRES_PASSWORD: Union[str, None] = None
    POSTGRES_DB: Union[str, None] = None
    POSTGRES_DATABASE: Union[str, None] = None

    @property
    def sync_database_url(self) -> str:
        # Check all possible sources for PostgreSQL / remote database connection strings
        candidates = [
            self.POSTGRES_URL,
            self.POSTGRES_PRISMA_URL,
            self.POSTGRES_URL_NON_POOLING,
            self.DATABASE_URL,
            os.environ.get("POSTGRES_URL"),
            os.environ.get("POSTGRES_PRISMA_URL"),
            os.environ.get("POSTGRES_URL_NON_POOLING"),
            os.environ.get("DATABASE_URL"),
        ]

        # Prioritize explicit PostgreSQL connection strings from any source
        for candidate in candidates:
            if candidate and (candidate.startswith("postgres://") or candidate.startswith("postgresql://")):
                url = candidate.strip()
                if url.startswith("postgres://"):
                    url = "postgresql://" + url[len("postgres://"):]
                return url

        # Check for non-relative SQLite or custom URLs
        for candidate in candidates:
            if candidate and not candidate.startswith("sqlite:///."):
                return candidate.strip()

        # Check for individual POSTGRES_* credentials
        host = self.POSTGRES_SERVER or self.POSTGRES_HOST or os.environ.get("POSTGRES_SERVER") or os.environ.get("POSTGRES_HOST")
        user = self.POSTGRES_USER or os.environ.get("POSTGRES_USER")
        password = self.POSTGRES_PASSWORD or os.environ.get("POSTGRES_PASSWORD")
        db_name = self.POSTGRES_DB or self.POSTGRES_DATABASE or os.environ.get("POSTGRES_DB") or os.environ.get("POSTGRES_DATABASE")
        port = self.POSTGRES_PORT or int(os.environ.get("POSTGRES_PORT", 5432))

        if host and user and password and db_name:
            return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

        # If in Vercel or AWS Lambda serverless read-only environment and no external database URL is configured
        if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            tmp_db = "/tmp/skillbridge.db"
            if not os.path.exists(tmp_db):
                for candidate_file in ["skillbridge.db", "backend/skillbridge.db", "../backend/skillbridge.db"]:
                    if os.path.exists(candidate_file):
                        try:
                            shutil.copy2(candidate_file, tmp_db)
                            break
                        except Exception:
                            pass
            return f"sqlite:///{tmp_db}"

        return self.DATABASE_URL or "sqlite:///./skillbridge.db"

    @property
    def is_persistent_db(self) -> bool:
        """Determines if the active database is persistent across serverless invocations."""
        url = self.sync_database_url
        if url.startswith("postgresql") or url.startswith("postgres"):
            return True
        if "sqlite" in url and not url.startswith("sqlite:////tmp"):
            # Local filesystem SQLite is persistent locally, but ephemeral in serverless /tmp
            return not bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
        return False

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
            ".env",
            "backend/.env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
