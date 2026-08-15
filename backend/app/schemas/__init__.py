"""Pydantic schemas package."""
from .health import HealthResponse
from .student import StudentBase, StudentCreate, StudentRead, StudentDetailRead
from .skill import SkillBase, SkillCreate, SkillRead, StudentSkillBase, StudentSkillCreate, StudentSkillRead
from .evidence import EvidenceType, EvidenceBase, EvidenceCreate, EvidenceRead
from .internship import InternshipBase, InternshipCreate, InternshipRead, InternshipSkillBase, InternshipSkillCreate, InternshipSkillRead
from .match import MatchExplanation, MatchRead
from .recommendation import (
    SupportingEvidenceDetail,
    MatchedSkillDetail,
    InsufficientSkillDetail,
    UnverifiedSkillDetail,
    RecommendationRead,
    StudentRecommendationsResponse,
)

__all__ = [
    "HealthResponse",
    "StudentBase",
    "StudentCreate",
    "StudentRead",
    "StudentDetailRead",
    "SkillBase",
    "SkillCreate",
    "SkillRead",
    "StudentSkillBase",
    "StudentSkillCreate",
    "StudentSkillRead",
    "EvidenceType",
    "EvidenceBase",
    "EvidenceCreate",
    "EvidenceRead",
    "InternshipBase",
    "InternshipCreate",
    "InternshipRead",
    "InternshipSkillBase",
    "InternshipSkillCreate",
    "InternshipSkillRead",
    "MatchExplanation",
    "MatchRead",
    "SupportingEvidenceDetail",
    "MatchedSkillDetail",
    "InsufficientSkillDetail",
    "UnverifiedSkillDetail",
    "RecommendationRead",
    "StudentRecommendationsResponse",
]
