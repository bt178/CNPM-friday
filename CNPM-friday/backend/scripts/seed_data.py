"""
Seed script to create test accounts and data.
Run: python -m scripts.seed_data
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.all_models import (
    Role,
    User,
    Department,
    Semester,
    Subject,
    AcademicClass,
    ClassEnrollment,
    Team,
    TeamMember,
)
from app.core.security import get_password_hash


DEFAULT_PASSWORD = "Password123!"
DEFAULT_PASSWORD_HASH = get_password_hash(DEFAULT_PASSWORD)


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


async def seed_semesters():
    """Seed a default semester."""
    async with AsyncSessionLocal() as db:
        semester = Semester(
            semester_id=1,
            semester_code="2025-FALL",
            start_date=None,
            end_date=None,
            status="ACTIVE",
        )
        existing = await db.get(Semester, semester.semester_id)
        if not existing:
            db.add(semester)
            await db.commit()
            print("✅ Semester seeded")
        else:
            print("ℹ️ Semester exists")


async def seed_subjects():
    """Seed a default subject."""
    async with AsyncSessionLocal() as db:
        subject = Subject(
            subject_id=1,
            subject_code="IT101",
            subject_name="Intro to IT",
            dept_id=1,
        )
        existing = await db.get(Subject, subject.subject_id)
        if not existing:
            db.add(subject)
            await db.commit()
            print("✅ Subject seeded")
        else:
            print("ℹ️ Subject exists")


async def seed_test_users():
    """Seed test users for each role."""
    async with AsyncSessionLocal() as db:
        test_users = [
            # ADMINS (2)
            {
                "email": "admin1@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Admin One",
                "role_id": 1,
                "is_active": True,
            },
            {
                "email": "admin2@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Admin Two",
                "role_id": 1,
                "is_active": True,
            },
            # STAFF (3)
            {
                "email": "staff1@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Staff One",
                "role_id": 2,
                "dept_id": 1,
                "is_active": True,
            },
            {
                "email": "staff2@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Staff Two",
                "role_id": 2,
                "dept_id": 2,
                "is_active": True,
            },
            {
                "email": "staff3@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Staff Three",
                "role_id": 2,
                "dept_id": 1,
                "is_active": True,
            },
            # HEAD_DEPT (2)
            {
                "email": "hod1@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Head of Department One",
                "role_id": 3,
                "dept_id": 1,
                "is_active": True,
            },
            {
                "email": "hod2@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Head of Department Two",
                "role_id": 3,
                "dept_id": 2,
                "is_active": True,
            },
            # LECTURERS (2)
            {
                "email": "lect1@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Lecturer One",
                "role_id": 4,
                "dept_id": 1,
                "is_active": True,
            },
            {
                "email": "lect2@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Lecturer Two",
                "role_id": 4,
                "dept_id": 2,
                "is_active": True,
            },
            # STUDENTS (5) — first is intended leader when you add team memberships
            {
                "email": "student1@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Student One (Leader)",
                "role_id": 5,
                "dept_id": 1,
                "is_active": True,
            },
            {
                "email": "student2@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Student Two",
                "role_id": 5,
                "dept_id": 1,
                "is_active": True,
            },
            {
                "email": "student3@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Student Three",
                "role_id": 5,
                "dept_id": 2,
                "is_active": True,
            },
            {
                "email": "student4@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Student Four",
                "role_id": 5,
                "dept_id": 2,
                "is_active": True,
            },
            {
                "email": "student5@collabsphere.com",
                "password_hash": DEFAULT_PASSWORD_HASH,
                "full_name": "Student Five",
                "role_id": 5,
                "dept_id": 1,
                "is_active": True,
            },
        ]
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


async def seed_academic_class():
    """Seed a default academic class using lecturer lect1@collabsphere.com."""
    async with AsyncSessionLocal() as db:
        lecturer = await db.scalar(select(User).where(User.email == "lect1@collabsphere.com"))
        if not lecturer:
            print("⚠️ Lecturer lect1@collabsphere.com not found; skip class seed")
            return

        existing = await db.scalar(select(AcademicClass).where(AcademicClass.class_code == "IT101-01"))
        if existing:
            print("ℹ️ Academic class exists")
            return

        academic_class = AcademicClass(
            class_code="IT101-01",
            semester_id=1,
            subject_id=1,
            lecturer_id=lecturer.user_id,
        )
        db.add(academic_class)
        await db.commit()
        print("✅ Academic class seeded (IT101-01)")


async def seed_enrollments_and_team():
    """Enroll students to class and create a team with leader stud1."""
    async with AsyncSessionLocal() as db:
        # Fetch class
        academic_class = await db.scalar(select(AcademicClass).where(AcademicClass.class_code == "IT101-01"))
        if not academic_class:
            print("⚠️ Academic class IT101-01 missing; skip team seed")
            return

        # Fetch students
        student_emails = [
            "student1@collabsphere.com",
            "student2@collabsphere.com",
            "student3@collabsphere.com",
            "student4@collabsphere.com",
            "student5@collabsphere.com",
        ]
        students = {
            u.email: u
            for u in (await db.scalars(select(User).where(User.email.in_(student_emails)))).all()
        }
        if len(students) != len(student_emails):
            print("⚠️ Not all student accounts exist; skip team seed")
            return

        # Enroll students into the class if not already
        for email, user in students.items():
            exists = await db.scalar(
                select(ClassEnrollment).where(
                    ClassEnrollment.class_id == academic_class.class_id,
                    ClassEnrollment.student_id == user.user_id,
                )
            )
            if not exists:
                db.add(ClassEnrollment(class_id=academic_class.class_id, student_id=user.user_id))

        await db.commit()

        # Create team with student1 as leader
        leader = students["student1@collabsphere.com"]
        team_exists = await db.scalar(select(Team).where(Team.class_id == academic_class.class_id))
        if not team_exists:
            team = Team(
                class_id=academic_class.class_id,
                leader_id=leader.user_id,
                team_name="Team Alpha",
                join_code="TEAM123",
            )
            db.add(team)
            await db.flush()  # get team_id

            # Add members
            for email, user in students.items():
                role = "LEADER" if email == "student1@collabsphere.com" else "MEMBER"
                db.add(
                    TeamMember(
                        team_id=team.team_id,
                        student_id=user.user_id,
                        role=role,
                        is_active=True,
                    )
                )
            await db.commit()
            print("✅ Team seeded with members (Team Alpha, join_code=TEAM123)")
        else:
            print("ℹ️ Team already exists for class IT101-01")


async def main():
    print("\n🌱 Seeding database...")
    print("-" * 40)
    await seed_roles()
    await seed_departments()
    await seed_test_users()
    await seed_semesters()
    await seed_subjects()
    await seed_academic_class()
    await seed_enrollments_and_team()
    print("-" * 40)
    print("🎉 Done!")
    print("\n📋 TEST ACCOUNTS:")
    print("=" * 50)
    print("Password for all:", DEFAULT_PASSWORD)
    print("| Email                          | Role        |")
    print("|" + "-" * 50 + "|")
    print("| admin1@collabsphere.com        | ADMIN       |")
    print("| admin2@collabsphere.com        | ADMIN       |")
    print("| staff1@collabsphere.com        | STAFF       |")
    print("| staff2@collabsphere.com        | STAFF       |")
    print("| staff3@collabsphere.com        | STAFF       |")
    print("| hod1@collabsphere.com          | HEAD_DEPT   |")
    print("| hod2@collabsphere.com          | HEAD_DEPT   |")
    print("| lect1@collabsphere.com         | LECTURER    |")
    print("| lect2@collabsphere.com         | LECTURER    |")
    print("| student1@collabsphere.com      | STUDENT     | (leader)")
    print("| student2@collabsphere.com      | STUDENT     |")
    print("| student3@collabsphere.com      | STUDENT     |")
    print("| student4@collabsphere.com      | STUDENT     |")
    print("| student5@collabsphere.com      | STUDENT     |")
    print("=" * 50)
    print("Team: Team Alpha, join_code=TEAM123, class=IT101-01, leader=student1@collabsphere.com")


if __name__ == "__main__":
    asyncio.run(main())
