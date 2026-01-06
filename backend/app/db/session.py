"""Database session management for async SQLAlchemy operations."""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Test connections before use
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum number of connections that can be created beyond pool_size
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent automatic expiration of objects after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency function for FastAPI endpoints.
    Provides an async database session and handles cleanup.

    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # Session will be automatically closed by the async context manager
            pass