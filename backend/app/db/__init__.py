# app/db/__init__.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from .session import get_db  # Ensure get_db is imported correctly

# Setup the async database engine
DATABASE_URL = settings.DATABASE_URL  # Ensure the database URL is correctly set in the config
engine = create_async_engine(DATABASE_URL, echo=True)

# Session maker for async operations
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get the database session
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
