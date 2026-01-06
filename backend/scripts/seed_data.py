"""
Seed initial data for testing.
Creates roles, departments, test users, semesters, subjects, and classes.
"""
import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.all_models import (
    AcademicClass,
    Department,
    Role,
    Semester,
    Subject,
    User,
)


async def seed_all():
    """Seed all initial data."""
    async with AsyncSessionLocal() as db:
        print("\n🌱 Starting database seeding...")
        print("=" * 60)
        
        # 1. Create Roles
        print("\n📋 Creating roles...")
        roles_data = ["ADMIN", "STAFF", "HEAD_DEPT", "LECTURER", "STUDENT"]
        for role_name in roles_data:
            result = await db.execute(select(Role).where(Role.role_name == role_name))
            if not result.scalar_one_or_none():
                db.add(Role(role_name=role_name))
                print(f"  ✅ Created role: {role_name}")
            else:
                print(f"  ⏭️  Role already exists: {role_name}")
        await db.commit()
        
        # Get role IDs
        roles = {}
        result = await db.execute(select(Role))
        for role in result.scalars():
            roles[role.role_name] = role.role_id
        
        # 2. Create Department
        print("\n🏢 Creating departments...")
        dept_names = ["Software Engineering", "Computer Science", "Information Systems"]
        departments = []
        for dept_name in dept_names:
            result = await db.execute(select(Department).where(Department.dept_name == dept_name))
            dept = result.scalar_one_or_none()
            if not dept:
                dept = Department(dept_name=dept_name)
                db.add(dept)
                print(f"  ✅ Created department: {dept_name}")
            else:
                print(f"  ⏭️  Department already exists: {dept_name}")
            departments.append(dept)
        await db.commit()
        
        # Get first department
        result = await db.execute(select(Department).limit(1))
        dept = result.scalar_one()
        
        # 3. Create Users
        print("\n👥 Creating test users...")
        test_users = [
            {
                "email": "admin@university.edu",
                "password": "admin123",
                "full_name": "Admin User",
                "role": "ADMIN",
            },
            {
                "email": "head.dept@university.edu",
                "password": "head123",
                "full_name": "Head of Department",
                "role": "HEAD_DEPT",
            },
            {
                "email": "staff@university.edu",
                "password": "staff123",
                "full_name": "Academic Staff",
                "role": "STAFF",
            },
            {
                "email": "lecturer@university.edu",
                "password": "lecturer123",
                "full_name": "Dr. John Smith",
                "role": "LECTURER",
            },
            {
                "email": "lecturer2@university.edu",
                "password": "lecturer123",
                "full_name": "Dr. Jane Doe",
                "role": "LECTURER",
            },
            {
                "email": "student@university.edu",
                "password": "student123",
                "full_name": "Alice Student",
                "role": "STUDENT",
            },
            {
                "email": "student2@university.edu",
                "password": "student123",
                "full_name": "Bob Student",
                "role": "STUDENT",
            },
            {
                "email": "student3@university.edu",
                "password": "student123",
                "full_name": "Charlie Student",
                "role": "STUDENT",
            },
        ]
        
        for user_data in test_users:
            result = await db.execute(select(User).where(User.email == user_data["email"]))
            if not result.scalar_one_or_none():
                user = User(
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role_id=roles[user_data["role"]],
                    dept_id=dept.dept_id,
                    is_active=True,
                )
                db.add(user)
                print(f"  ✅ Created user: {user_data['email']} ({user_data['role']})")
            else:
                print(f"  ⏭️  User already exists: {user_data['email']}")
        await db.commit()
        
        # 4. Create Semester
        print("\n📅 Creating semesters...")
        semesters_data = [
            {
                "semester_code": "FALL2024",
                "start_date": date(2024, 9, 1),
                "end_date": date(2024, 12, 31),
                "status": "completed",
            },
            {
                "semester_code": "SPRING2025",
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 5, 31),
                "status": "active",
            },
        ]
        
        for sem_data in semesters_data:
            result = await db.execute(select(Semester).where(Semester.semester_code == sem_data["semester_code"]))
            if not result.scalar_one_or_none():
                semester = Semester(**sem_data)
                db.add(semester)
                print(f"  ✅ Created semester: {sem_data['semester_code']}")
            else:
                print(f"  ⏭️  Semester already exists: {sem_data['semester_code']}")
        await db.commit()
        
        # Get active semester
        result = await db.execute(
            select(Semester).where(Semester.status == "active").limit(1)
        )
        semester = result.scalar_one()
        
        # 5. Create Subjects
        print("\n📚 Creating subjects...")
        subjects_data = [
            {
                "subject_code": "SE1801",
                "subject_name": "Capstone Project",
                "dept_id": dept.dept_id,
            },
            {
                "subject_code": "PRN231",
                "subject_name": "Building Cross-Platform Apps",
                "dept_id": dept.dept_id,
            },
        ]
        
        for subj_data in subjects_data:
            result = await db.execute(select(Subject).where(Subject.subject_code == subj_data["subject_code"]))
            if not result.scalar_one_or_none():
                subject = Subject(**subj_data)
                db.add(subject)
                print(f"  ✅ Created subject: {subj_data['subject_code']}")
            else:
                print(f"  ⏭️  Subject already exists: {subj_data['subject_code']}")
        await db.commit()
        
        # Get first subject
        result = await db.execute(select(Subject).limit(1))
        subject = result.scalar_one()
        
        # 6. Create Classes
        print("\n🎓 Creating classes...")
        
        # Get lecturer
        lecturer_result = await db.execute(
            select(User)
            .join(User.role)
            .where(Role.role_name == "LECTURER")
            .limit(1)
        )
        lecturer = lecturer_result.scalar_one_or_none()
        
        if lecturer:
            classes_data = [
                {
                    "class_code": "SE1801_SP25_01",
                    "semester_id": semester.semester_id,
                    "subject_id": subject.subject_id,
                    "lecturer_id": lecturer.user_id,
                },
                {
                    "class_code": "SE1801_SP25_02",
                    "semester_id": semester.semester_id,
                    "subject_id": subject.subject_id,
                    "lecturer_id": lecturer.user_id,
                },
            ]
            
            for class_data in classes_data:
                result = await db.execute(
                    select(AcademicClass).where(AcademicClass.class_code == class_data["class_code"])
                )
                if not result.scalar_one_or_none():
                    academic_class = AcademicClass(**class_data)
                    db.add(academic_class)
                    print(f"  ✅ Created class: {class_data['class_code']}")
                else:
                    print(f"  ⏭️  Class already exists: {class_data['class_code']}")
            await db.commit()
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed!")
        print("=" * 60)
        print("\n🔑 Test Accounts:")
        print("=" * 60)
        print("ADMIN:     admin@university.edu / admin123")
        print("HEAD DEPT: head.dept@university.edu / head123")
        print("STAFF:     staff@university.edu / staff123")
        print("LECTURER:  lecturer@university.edu / lecturer123")
        print("LECTURER2: lecturer2@university.edu / lecturer123")
        print("STUDENT:   student@university.edu / student123")
        print("STUDENT2:  student2@university.edu / student123")
        print("STUDENT3:  student3@university.edu / student123")
        print("=" * 60)
        print("\n📍 API Docs: http://localhost:8000/docs")
        print("📍 Health Check: http://localhost:8000/health\n")


if __name__ == "__main__":
    try:
        asyncio.run(seed_all())
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        raise