"""
Submissions API Endpoints - Phase 4
Copy file này vào: backend/app/api/v1/submissions.py
Sau đó register router trong api.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.all_models import Submission, Milestone, Team, TeamMember, User

from pydantic import BaseModel, Field

# ========== SCHEMAS ==========

class SubmissionCreate(BaseModel):
    milestone_id: int
    team_id: int
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None  # Description or content of submission
    file_url: Optional[str] = None  # Link to uploaded file

class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    file_url: Optional[str] = None

class SubmissionGrade(BaseModel):
    score: float = Field(..., ge=0, le=10)
    feedback: Optional[str] = None

class SubmissionResponse(BaseModel):
    submission_id: int
    milestone_id: int
    team_id: int
    submitted_by: UUID
    submitter_name: Optional[str] = None
    title: str
    content: Optional[str]
    file_url: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    graded_by: Optional[UUID]
    grader_name: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SubmissionListResponse(BaseModel):
    submissions: List[SubmissionResponse]
    total: int

# ========== ROUTER ==========

router = APIRouter()


@router.post("/", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Nộp bài cho milestone.
    Chỉ team members mới có thể nộp.
    """
    # Kiểm tra milestone tồn tại
    milestone = await db.get(Milestone, submission_data.milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone không tồn tại"
        )
    
    # Kiểm tra user có phải team member không
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == submission_data.team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    if not member_check.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn phải là thành viên của team mới có thể nộp bài"
        )
    
    # Kiểm tra đã nộp chưa (mỗi team chỉ nộp 1 lần cho mỗi milestone)
    existing = await db.execute(
        select(Submission).where(
            Submission.milestone_id == submission_data.milestone_id,
            Submission.team_id == submission_data.team_id
        )
    )
    if existing.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team đã nộp bài cho milestone này rồi. Vui lòng cập nhật bài nộp thay vì tạo mới."
        )
    
    new_submission = Submission(
        milestone_id=submission_data.milestone_id,
        team_id=submission_data.team_id,
        submitted_by=current_user.user_id,
        title=submission_data.title,
        content=submission_data.content,
        file_url=submission_data.file_url,
        submitted_at=datetime.utcnow()
    )
    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)
    
    return SubmissionResponse(
        submission_id=new_submission.submission_id,
        milestone_id=new_submission.milestone_id,
        team_id=new_submission.team_id,
        submitted_by=new_submission.submitted_by,
        submitter_name=current_user.full_name,
        title=new_submission.title,
        content=new_submission.content,
        file_url=new_submission.file_url,
        score=new_submission.score,
        feedback=new_submission.feedback,
        graded_by=new_submission.graded_by,
        grader_name=None,
        submitted_at=new_submission.submitted_at,
        graded_at=new_submission.graded_at
    )


@router.get("/", response_model=SubmissionListResponse)
async def list_submissions(
    milestone_id: Optional[int] = None,
    team_id: Optional[int] = None,
    graded_only: bool = Query(False, description="Chỉ lấy submissions đã chấm"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách submissions.
    Có thể filter theo milestone_id hoặc team_id.
    """
    query = select(Submission)
    
    if milestone_id:
        query = query.where(Submission.milestone_id == milestone_id)
    if team_id:
        query = query.where(Submission.team_id == team_id)
    if graded_only:
        query = query.where(Submission.score.isnot(None))
    
    # Pagination
    offset = (page - 1) * limit
    query = query.order_by(Submission.submitted_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    # Count total
    count_query = select(Submission)
    if milestone_id:
        count_query = count_query.where(Submission.milestone_id == milestone_id)
    if team_id:
        count_query = count_query.where(Submission.team_id == team_id)
    if graded_only:
        count_query = count_query.where(Submission.score.isnot(None))
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    response = []
    for submission in submissions:
        submitter = await db.get(User, submission.submitted_by)
        grader = await db.get(User, submission.graded_by) if submission.graded_by else None
        
        response.append(SubmissionResponse(
            submission_id=submission.submission_id,
            milestone_id=submission.milestone_id,
            team_id=submission.team_id,
            submitted_by=submission.submitted_by,
            submitter_name=submitter.full_name if submitter else "Unknown",
            title=submission.title,
            content=submission.content,
            file_url=submission.file_url,
            score=submission.score,
            feedback=submission.feedback,
            graded_by=submission.graded_by,
            grader_name=grader.full_name if grader else None,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at
        ))
    
    return SubmissionListResponse(submissions=response, total=total)


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy chi tiết submission."""
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission không tồn tại"
        )
    
    submitter = await db.get(User, submission.submitted_by)
    grader = await db.get(User, submission.graded_by) if submission.graded_by else None
    
    return SubmissionResponse(
        submission_id=submission.submission_id,
        milestone_id=submission.milestone_id,
        team_id=submission.team_id,
        submitted_by=submission.submitted_by,
        submitter_name=submitter.full_name if submitter else "Unknown",
        title=submission.title,
        content=submission.content,
        file_url=submission.file_url,
        score=submission.score,
        feedback=submission.feedback,
        graded_by=submission.graded_by,
        grader_name=grader.full_name if grader else None,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at
    )


@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: int,
    update_data: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật submission.
    Chỉ team members và chưa được chấm điểm mới có thể cập nhật.
    """
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission không tồn tại"
        )
    
    # Kiểm tra đã chấm điểm chưa
    if submission.score is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể cập nhật submission đã được chấm điểm"
        )
    
    # Kiểm tra có phải team member không
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == submission.team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    if not member_check.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền cập nhật submission này"
        )
    
    if update_data.title is not None:
        submission.title = update_data.title
    if update_data.content is not None:
        submission.content = update_data.content
    if update_data.file_url is not None:
        submission.file_url = update_data.file_url
    
    await db.commit()
    await db.refresh(submission)
    
    submitter = await db.get(User, submission.submitted_by)
    
    return SubmissionResponse(
        submission_id=submission.submission_id,
        milestone_id=submission.milestone_id,
        team_id=submission.team_id,
        submitted_by=submission.submitted_by,
        submitter_name=submitter.full_name if submitter else "Unknown",
        title=submission.title,
        content=submission.content,
        file_url=submission.file_url,
        score=submission.score,
        feedback=submission.feedback,
        graded_by=submission.graded_by,
        grader_name=None,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at
    )


@router.post("/{submission_id}/grade", response_model=SubmissionResponse)
async def grade_submission(
    submission_id: int,
    grade_data: SubmissionGrade,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chấm điểm submission.
    Chỉ Lecturer (role_id=4) hoặc Admin mới có quyền chấm.
    """
    if current_user.role_id not in [1, 4]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Lecturer mới có quyền chấm điểm"
        )
    
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission không tồn tại"
        )
    
    submission.score = grade_data.score
    submission.feedback = grade_data.feedback
    submission.graded_by = current_user.user_id
    submission.graded_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(submission)
    
    submitter = await db.get(User, submission.submitted_by)
    
    return SubmissionResponse(
        submission_id=submission.submission_id,
        milestone_id=submission.milestone_id,
        team_id=submission.team_id,
        submitted_by=submission.submitted_by,
        submitter_name=submitter.full_name if submitter else "Unknown",
        title=submission.title,
        content=submission.content,
        file_url=submission.file_url,
        score=submission.score,
        feedback=submission.feedback,
        graded_by=submission.graded_by,
        grader_name=current_user.full_name,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at
    )


@router.delete("/{submission_id}", status_code=204)
async def delete_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Xóa submission.
    Chỉ có thể xóa nếu chưa được chấm điểm.
    """
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission không tồn tại"
        )
    
    if submission.score is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa submission đã được chấm điểm"
        )
    
    # Chỉ team member hoặc admin mới xóa được
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == submission.team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    is_member = member_check.scalar() is not None
    
    if not is_member and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa submission này"
        )
    
    await db.delete(submission)
    await db.commit()
    return None
