from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models.all_models import Semester
from app.schemas.semesters import SemesterCreate, SemesterUpdate, SemesterResponse

router = APIRouter()

@router.post("/", response_model=SemesterResponse, status_code=201)
async def create_semester(
    semester_in: SemesterCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check duplicate semester_code
    check_query = select(Semester).where(Semester.semester_code == semester_in.semester_code)
    result = await db.execute(check_query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Semester with code '{semester_in.semester_code}' already exists"
        )
    
    db_semester = Semester(
        semester_code=semester_in.semester_code,  # ✅ THÊM
        semester_name=semester_in.semester_name,
        start_date=semester_in.start_date,
        end_date=semester_in.end_date,
        status=semester_in.status  # ✅ THÊM
    )
    
    db.add(db_semester)
    await db.commit()
    await db.refresh(db_semester)
    
    return db_semester