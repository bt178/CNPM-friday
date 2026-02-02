"""
AI Mentoring API Endpoints - Phase 4
Copy file này vào: backend/app/api/v1/mentoring.py
Sau đó register router trong api.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.all_models import MentoringLog, Team, TeamMember, User
from app.services.ai_service import get_ai_suggestions

from pydantic import BaseModel, Field

# ========== SCHEMAS ==========

class MentoringLogCreate(BaseModel):
    team_id: int
    session_notes: Optional[str] = None
    discussion_points: Optional[str] = None
    meeting_date: Optional[datetime] = None

class MentoringLogUpdate(BaseModel):
    session_notes: Optional[str] = None
    discussion_points: Optional[str] = None
    feedback: Optional[str] = None

class MentoringLogResponse(BaseModel):
    log_id: int
    team_id: int
    mentor_id: UUID
    mentor_name: Optional[str] = None
    session_notes: Optional[str]
    discussion_points: Optional[str]
    ai_suggestions: Optional[str]
    feedback: Optional[str]
    meeting_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AISuggestionRequest(BaseModel):
    team_id: int
    context: Optional[str] = None  # Additional context for AI

class AISuggestionResponse(BaseModel):
    suggestions: str
    generated_at: datetime
    context_used: Optional[str] = None

# ========== ROUTER ==========

router = APIRouter()


@router.post("/", response_model=MentoringLogResponse, status_code=201)
async def create_mentoring_log(
    log_data: MentoringLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo mentoring log mới.
    Chỉ Lecturer (role_id=4) hoặc Admin mới có thể tạo.
    """
    # Kiểm tra role
    if current_user.role_id not in [1, 4]:  # Admin or Lecturer
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Lecturer mới có thể tạo mentoring log"
        )
    
    # Kiểm tra team tồn tại
    team = await db.get(Team, log_data.team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team không tồn tại"
        )
    
    # Tạo log
    new_log = MentoringLog(
        team_id=log_data.team_id,
        mentor_id=current_user.user_id,
        session_notes=log_data.session_notes,
        discussion_points=log_data.discussion_points,
        meeting_date=log_data.meeting_date or datetime.utcnow()
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    
    return MentoringLogResponse(
        log_id=new_log.log_id,
        team_id=new_log.team_id,
        mentor_id=new_log.mentor_id,
        mentor_name=current_user.full_name,
        session_notes=new_log.session_notes,
        discussion_points=new_log.discussion_points,
        ai_suggestions=new_log.ai_suggestions,
        feedback=new_log.feedback,
        meeting_date=new_log.meeting_date,
        created_at=new_log.created_at
    )


@router.get("/", response_model=List[MentoringLogResponse])
async def list_mentoring_logs(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách mentoring logs của team.
    """
    # Kiểm tra user có phải team member hoặc lecturer không
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    is_member = member_check.scalar() is not None
    is_lecturer = current_user.role_id in [1, 4]  # Admin or Lecturer
    
    if not is_member and not is_lecturer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem mentoring logs của team này"
        )
    
    result = await db.execute(
        select(MentoringLog)
        .where(MentoringLog.team_id == team_id)
        .order_by(MentoringLog.created_at.desc())
    )
    logs = result.scalars().all()
    
    response = []
    for log in logs:
        mentor = await db.get(User, log.mentor_id)
        response.append(MentoringLogResponse(
            log_id=log.log_id,
            team_id=log.team_id,
            mentor_id=log.mentor_id,
            mentor_name=mentor.full_name if mentor else "Unknown",
            session_notes=log.session_notes,
            discussion_points=log.discussion_points,
            ai_suggestions=log.ai_suggestions,
            feedback=log.feedback,
            meeting_date=log.meeting_date,
            created_at=log.created_at
        ))
    
    return response


@router.get("/{log_id}", response_model=MentoringLogResponse)
async def get_mentoring_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy chi tiết mentoring log."""
    log = await db.get(MentoringLog, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentoring log không tồn tại"
        )
    
    mentor = await db.get(User, log.mentor_id)
    
    return MentoringLogResponse(
        log_id=log.log_id,
        team_id=log.team_id,
        mentor_id=log.mentor_id,
        mentor_name=mentor.full_name if mentor else "Unknown",
        session_notes=log.session_notes,
        discussion_points=log.discussion_points,
        ai_suggestions=log.ai_suggestions,
        feedback=log.feedback,
        meeting_date=log.meeting_date,
        created_at=log.created_at
    )


@router.put("/{log_id}", response_model=MentoringLogResponse)
async def update_mentoring_log(
    log_id: int,
    update_data: MentoringLogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật mentoring log.
    Chỉ mentor của log mới có quyền cập nhật.
    """
    log = await db.get(MentoringLog, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentoring log không tồn tại"
        )
    
    if log.mentor_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ mentor mới có quyền cập nhật log này"
        )
    
    if update_data.session_notes is not None:
        log.session_notes = update_data.session_notes
    if update_data.discussion_points is not None:
        log.discussion_points = update_data.discussion_points
    if update_data.feedback is not None:
        log.feedback = update_data.feedback
    
    await db.commit()
    await db.refresh(log)
    
    return MentoringLogResponse(
        log_id=log.log_id,
        team_id=log.team_id,
        mentor_id=log.mentor_id,
        mentor_name=current_user.full_name,
        session_notes=log.session_notes,
        discussion_points=log.discussion_points,
        ai_suggestions=log.ai_suggestions,
        feedback=log.feedback,
        meeting_date=log.meeting_date,
        created_at=log.created_at
    )


@router.post("/{log_id}/ai-suggestions", response_model=AISuggestionResponse)
async def generate_ai_suggestions(
    log_id: int,
    request: AISuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo AI suggestions cho mentoring log.
    Sử dụng Google Gemini API.
    """
    log = await db.get(MentoringLog, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentoring log không tồn tại"
        )
    
    # Xây dựng context cho AI
    context = f"""
    Team ID: {log.team_id}
    Session Notes: {log.session_notes or 'N/A'}
    Discussion Points: {log.discussion_points or 'N/A'}
    Additional Context: {request.context or 'None'}
    """
    
    try:
        # Gọi AI service
        suggestions = await get_ai_suggestions(context)
        
        # Lưu suggestions vào log
        log.ai_suggestions = suggestions
        await db.commit()
        
        return AISuggestionResponse(
            suggestions=suggestions,
            generated_at=datetime.utcnow(),
            context_used=context.strip()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI suggestions: {str(e)}"
        )


@router.delete("/{log_id}", status_code=204)
async def delete_mentoring_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa mentoring log.
    Chỉ mentor của log mới có quyền xóa.
    """
    log = await db.get(MentoringLog, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentoring log không tồn tại"
        )
    
    if log.mentor_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ mentor mới có quyền xóa log này"
        )
    
    await db.delete(log)
    await db.commit()
    return None
