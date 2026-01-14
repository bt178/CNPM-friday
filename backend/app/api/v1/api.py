"""Main API router for version 1 endpoints."""

from fastapi import APIRouter
from app.api.v1 import (
    departments, 
    subjects,
    semesters,
    academic_classes,
    class_enrollments,
    syllabuses
    )

# Create the main API router
api_router = APIRouter()

# Auth 
from app.api.v1.auth import router as auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Academic Management endpoints
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(semesters.router, prefix="/semesters", tags=["semesters"])
api_router.include_router(academic_classes.router, prefix="/academic_classes", tags=["academic_classes"])
api_router.include_router(class_enrollments.router, prefix="/class_enrollments", tags=["class_enrollments"])
api_router.include_router(syllabuses.router, prefix="/syllabuses", tags=["syllabuses"])

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

# Example structure for future endpoints:
# from app.api.v1 import users, projects
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

api_router.include_router(profile.router, tags=["Profile"])
api_router.include_router(user_import.router, tags=["User Import"])
api_router.include_router(notifications.router, tags=["Notifications"])
