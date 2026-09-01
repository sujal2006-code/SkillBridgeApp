from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.init_db import ensure_db_initialized
from app.routes.health import router as health_router
from app.routes.students import router as students_router
from app.routes.skills import router as skills_router
from app.routes.evidence import router as evidence_router
from app.routes.internships import router as internships_router
from app.routes.recommendations import router as recommendations_router
from app.routes.teams import router as teams_router
from app.routes.activities import router as activities_router
from app.routes.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown events."""
    # Initialize database tables and seed demo data on startup
    ensure_db_initialized()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# First-request lazy initialization guarantee for serverless (Vercel) where lifespan may be skipped
@app.middleware("http")
async def ensure_db_middleware(request: Request, call_next):
    ensure_db_initialized()
    response = await call_next(request)
    return response

# CORS configuration allowing localhost and vercel.app origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

ROUTERS = [
    health_router,
    students_router,
    skills_router,
    evidence_router,
    internships_router,
    recommendations_router,
    teams_router,
    activities_router,
    admin_router,
]

# Include API Routers under /api (standard for local dev & explicit paths)
for r in ROUTERS:
    app.include_router(r, prefix=settings.API_V1_STR)

# Also include API Routers under root prefix (handles Vercel rewrite cases where /api is stripped)
for r in ROUTERS:
    app.include_router(r, prefix="")


@app.get("/")
def root():
    """Root endpoint providing links to API documentation and health status."""
    return {
        "message": "Welcome to the SkillBridge API",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health",
    }
