"""API routes package."""
from .health import router as health_router
from .students import router as students_router
from .skills import router as skills_router
from .evidence import router as evidence_router
from .internships import router as internships_router
from .recommendations import router as recommendations_router

__all__ = [
    "health_router",
    "students_router",
    "skills_router",
    "evidence_router",
    "internships_router",
    "recommendations_router",
]
