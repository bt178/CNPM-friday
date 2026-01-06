"""Main API router for version 1 endpoints."""

from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

# Auth endpoints
from app.api.v1.endpoints import auth
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Project & Team Module endpoints
from app.api.v1.endpoints import projects, teams, tasks

api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["Projects & Topics"],
)

api_router.include_router(
    teams.router,
    prefix="/teams",
    tags=["Teams"],
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Task Board"],
)

# Test endpoint
@api_router.get("/test")
async def test_endpoint():
    return {"message": "API is working!"}