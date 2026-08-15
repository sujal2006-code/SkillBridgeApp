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
    POSTGRES_SERVER: Union[str, None] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: Union[str, None] = None
    POSTGRES_PASSWORD: Union[str, None] = None
    POSTGRES_DB: Union[str, None] = None
    DATABASE_URL: Union[str, None] = "sqlite:///./skillbridge.db"

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.POSTGRES_SERVER and self.POSTGRES_USER and self.POSTGRES_PASSWORD and self.POSTGRES_DB:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return "sqlite:///./skillbridge.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
