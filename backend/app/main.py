from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base

from app.core.config import settings
from app.api.v1.api import api_router  # <--- Import cái router tổng vào
from app.db.base import Base
from app.db.session import engine
from app.models import all_models  # noqa: F401  # Ensure models register with Base
from app.models.all_models import Role

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Project-Based Learning Management System",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Configure CORS
# SỬA LỖI: Dùng đúng tên biến BACKEND_CORS_ORIGINS trong config.py
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# KẾT NỐI ROUTER (QUAN TRỌNG NHẤT)
# Dòng này sẽ đưa các API auth/login vào hệ thống
app.include_router(api_router, prefix=settings.API_V1_STR)


DEFAULT_ROLES = [
    {"role_id": 1, "role_name": "Admin"},
    {"role_id": 2, "role_name": "Staff"},
    {"role_id": 3, "role_name": "Head_Dept"},
    {"role_id": 4, "role_name": "Lecturer"},
    {"role_id": 5, "role_name": "Student"},
]


@app.on_event("startup")
async def on_startup() -> None:
    """Ensure database schema and seed data are present before serving requests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Seed default roles to satisfy FK constraints
        for role in DEFAULT_ROLES:
            stmt = (
                insert(Role)
                .values(**role)
                .on_conflict_do_nothing(index_elements=[Role.role_id])
            )
            await conn.execute(stmt)

@app.get("/test")
async def test():
    return {"message": "Test from main.py"}

@app.get("/")
async def root():
    """Root endpoint to verify the backend is running."""
    return {
        "message": "Hello from CollabSphere Backend",
        "docs_url": "Go to /docs to see Swagger UI"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}