"""
Initialize database - Create all tables automatically.
Replaces Alembic for quick development setup.
"""
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base

# Import all models to register them with Base
from app.models.all_models import *  # noqa


async def init_db():
    """Create all database tables."""
    print("🔧 Connecting to database...")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # Show SQL queries
    )
    
    print("\n📋 Creating database tables...")
    
    async with engine.begin() as conn:
        # Drop all tables first (for clean development)
        # Comment this out in production!
        print("⚠️  Dropping existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        print("✨ Creating fresh tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    
    print("\n✅ Database tables created successfully!")
    print("=" * 60)


def main():
    """Run database initialization."""
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        raise


if __name__ == "__main__":
    main()