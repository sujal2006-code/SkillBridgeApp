from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "SkillBridge API"
    version: str = "1.0.0"
