import asyncio
import logging
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.session import engine, AsyncSessionLocal
from app.models.all_models import Role, User, Department

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use local context with sha256_crypt to bypass bcrypt issues in container
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def seed_data():
    logger.info("Starting database seeding...")
    async with AsyncSessionLocal() as session:
        # 1. Seed Roles
        roles = ["ADMIN", "STAFF", "HEAD_DEPT", "LECTURER", "STUDENT"]
        role_map = {}
        for role_name in roles:
            stmt = select(Role).filter_by(role_name=role_name)
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            if not role:
                role = Role(role_name=role_name)
                session.add(role)
                await session.flush()  # Flush to get ID
                logger.info(f"Created role: {role_name}")
            role_map[role_name] = role.role_id

        # 2. Seed Departments
        depts = ["Software Engineering", "Computer Science", "Information Systems"]
        dept_map = {}
        for dept_name in depts:
            stmt = select(Department).filter_by(dept_name=dept_name)
            result = await session.execute(stmt)
            dept = result.scalar_one_or_none()
            if not dept:
                dept = Department(dept_name=dept_name)
                session.add(dept)
                await session.flush()
                logger.info(f"Created department: {dept_name}")
            dept_map[dept_name] = dept.dept_id

        # 3. Seed Admin User
        admin_email = "admin@example.com"
        stmt = select(User).filter_by(email=admin_email)
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                full_name="System Administrator",
                role_id=role_map["ADMIN"],
                is_active=True
            )
            session.add(admin)
            logger.info(f"Created admin user: {admin_email}")
        
        await session.commit()
        logger.info("Seeding completed successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())
