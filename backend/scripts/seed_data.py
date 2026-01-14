"""
Seed script to create test accounts and data.
Run: python -m scripts.seed_data
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.all_models import Role, User, Department, Semester, Subject, AcademicClass
from app.core.security import get_password_hash


async def seed_roles():
    """Seed roles if not exists."""
    async with AsyncSessionLocal() as db:
        roles = [
            {"role_id": 1, "role_name": "ADMIN"},
            {"role_id": 2, "role_name": "STAFF"},
            {"role_id": 3, "role_name": "HEAD_DEPT"},
            {"role_id": 4, "role_name": "LECTURER"},
            {"role_id": 5, "role_name": "STUDENT"},
        ]
        for role_data in roles:
            existing = await db.get(Role, role_data["role_id"])
            if not existing:
                db.add(Role(**role_data))
        await db.commit()
        print("✅ Roles seeded")


async def seed_departments():
    """Seed departments."""
    async with AsyncSessionLocal() as db:
        depts = [
            {"dept_id": 1, "dept_name": "Information Technology"},
            {"dept_id": 2, "dept_name": "Computer Science"},
        ]
        for dept_data in depts:
            existing = await db.get(Department, dept_data["dept_id"])
            if not existing:
                db.add(Department(**dept_data))
        await db.commit()
        print("✅ Departments seeded")


async def seed_test_users():
    """Seed test users for each role."""
    async with AsyncSessionLocal() as db:
        test_users = [
            # ADMIN
            {
                "email": "admin@collabsphere.com",
                "password_hash": get_password_hash("admin123"),
                "full_name": "Admin User",
                "role_id": 1,
                "is_active": True,
            },
            # HEAD_DEPT
            {
                "email": "head@collabsphere.com",
                "password_hash": get_password_hash("head123"),
                "full_name": "Head of Department",
                "role_id": 3,
                "dept_id": 1,
                "is_active": True,
            },
            # LECTURER
            {
                "email": "lecturer@collabsphere.com",
                "password_hash": get_password_hash("lecturer123"),
                "full_name": "Test Lecturer",
                "role_id": 4,
                "dept_id": 1,
                "is_active": True,
            },
            # STUDENTS
            {
                "email": "student1@collabsphere.com",
                "password_hash": get_password_hash("student123"),
                "full_name": "Student One",
                "role_id": 5,
                "dept_id": 1,
                "is_active": True,
            },
            {
                "email": "student2@collabsphere.com",
                "password_hash": get_password_hash("student123"),
                "full_name": "Student Two",
                "role_id": 5,
                "dept_id": 1,
                "is_active": True,
            },
        ]
        
        from sqlalchemy import select
        for user_data in test_users:
            result = await db.execute(select(User).where(User.email == user_data["email"]))
            existing = result.scalars().first()
            if not existing:
                db.add(User(**user_data))
                print(f"  Created: {user_data['email']}")
            else:
                print(f"  Exists: {user_data['email']}")
        
        await db.commit()
        print("✅ Test users seeded")


async def main():
    print("\n🌱 Seeding database...")
    print("-" * 40)
    await seed_roles()
    await seed_departments()
    await seed_test_users()
    print("-" * 40)
    print("🎉 Done!")
    print("\n📋 TEST ACCOUNTS:")
    print("=" * 50)
    print("| Email                      | Password     | Role      |")
    print("|" + "-" * 50 + "|")
    print("| admin@collabsphere.com     | admin123     | ADMIN     |")
    print("| head@collabsphere.com      | head123      | HEAD_DEPT |")
    print("| lecturer@collabsphere.com  | lecturer123  | LECTURER  |")
    print("| student1@collabsphere.com  | student123   | STUDENT   |")
    print("| student2@collabsphere.com  | student123   | STUDENT   |")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
