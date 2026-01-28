"""Main API router for version 1 endpoints."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db.session import AsyncSessionLocal, engine
from app.models.all_models import Base, Role

# Create the main API router
api_router = APIRouter()

# Include endpoint routers as they become available
# For now, we'll start with a basic structure
# TODO: Add more endpoint routers as they are implemented

# Auth 
from app.api.v1.auth import router as auth_router
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

from app.api.v1 import users
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Topics & Evaluation
from app.api.v1.topics import router as topics_router
api_router.include_router(topics_router, prefix="/topics", tags=["topics"])

# Teams
from app.api.v1.teams import router as teams_router
api_router.include_router(teams_router, prefix="/teams", tags=["teams"])

# Tasks & Sprints
from app.api.v1.tasks import router as tasks_router
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

# ===== ADMIN ENDPOINTS (Development Only) =====
@api_router.post("/admin/init-db", tags=["admin"])
async def initialize_database():
    """
    Create all tables and seed initial data.
    ⚠️ USE ONLY IN DEVELOPMENT!
    """
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Insert default roles
        async with AsyncSessionLocal() as db:
            # Check if roles already exist
            result = await db.execute(text("SELECT COUNT(*) FROM roles"))
            count = result.scalar()
            
            if count == 0:
                roles_data = [
                    Role(role_id=1, role_name="Admin"),
                    Role(role_id=2, role_name="Staff"),
                    Role(role_id=3, role_name="Head_Dept"),
                    Role(role_id=4, role_name="Lecturer"),
                    Role(role_id=5, role_name="Student"),
                ]
                db.add_all(roles_data)
                await db.commit()
                
                return {
                    "message": "Database initialized successfully",
                    "tables_created": True,
                    "roles_inserted": 5
                }
            else:
                return {
                    "message": "Database already initialized",
                    "tables_created": True,
                    "roles_existing": count
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")


@api_router.get("/admin/db-status", tags=["admin"])
async def check_database_status():
    """Check if database tables exist."""
    try:
        async with AsyncSessionLocal() as db:
            # Try to count roles
            result = await db.execute(text("SELECT COUNT(*) FROM roles"))
            roles_count = result.scalar()
            
            # Try to count users
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            
            return {
                "status": "healthy",
                "roles": roles_count,
                "users": users_count
            }
    except Exception as e:
        return {
            "status": "not_initialized",
            "error": str(e)
        }

# Test endpoint
@api_router.get("/test", tags=["system"])
async def test_endpoint():
    return {"message": "Test endpoint works"}
