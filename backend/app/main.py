from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base

from app.core.config import settings
from app.api.v1.api import api_router  # <--- Import cái router tổng vào

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