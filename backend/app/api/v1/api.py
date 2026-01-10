"""Main API router for version 1 endpoints."""

from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

# Auth 
from app.api.v1.auth import router as auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Topics (BE-PROJ-01)
from app.api.v1.endpoints.topics import router as topics_router
api_router.include_router(topics_router, prefix="/topics", tags=["topics"])

# Teams (BE-TEAM-01)
from app.api.v1.endpoints.teams import router as teams_router
api_router.include_router(teams_router, prefix="/teams", tags=["teams"])

# Tasks (BE-TASK-01)
from app.api.v1.endpoints.tasks import router as tasks_router
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

# Test endpoint
@api_router.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint works"}