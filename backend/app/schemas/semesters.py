from pydantic import BaseModel
from datetime import date
from typing import Optional

class SemesterCreate(BaseModel):
    semester_code: str  # ✅ THÊM - VD: "2026S1", "2026F1"
    semester_name: str  # VD: "Spring 2026"
    start_date: date
    end_date: date
    status: Optional[str] = None

class SemesterUpdate(BaseModel):
    semester_code: Optional[str] = None  # ✅ THÊM
    semester_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class SemesterResponse(BaseModel):
    semester_id: int
    semester_code: str  # ✅ THÊM
    semester_name: str
    start_date: date
    end_date: date
    status: Optional[str] = None
    
    class Config:
        from_attributes = True