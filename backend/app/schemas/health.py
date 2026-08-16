from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "SkillBridge API"
    version: str = "1.0.0"
    db_status: str = "connected"
    db_dialect: str = "sqlite"
    is_persistent: bool = True
    environment: str = "local"

