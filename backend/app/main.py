from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.v1.api import api_router  # Import from v1 API router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Project-Based Learning Management System",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Log database configuration on startup
@app.on_event("startup")
async def startup_event():
    db_url = settings.DATABASE_URL
    # Hide password for security
    db_display = db_url.replace(db_url.split('@')[0].split('://')[1], '****:****')
    logger.info(f"🗄️ DATABASE_URL: {db_display}")
    logger.info(f"📍 Using API prefix: {settings.API_V1_STR}")

# Configure CORS
# Always fall back to permissive origins during local development if none are provided
allowed_origins = settings.BACKEND_CORS_ORIGINS or ["*"]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in allowed_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount API routes with /api/v1 prefix
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