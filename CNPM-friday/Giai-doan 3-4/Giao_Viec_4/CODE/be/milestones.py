"""
Milestones & Checkpoints API Endpoints - Phase 4
Copy file này vào: backend/app/api/v1/milestones.py
Sau đó register router trong api.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.all_models import Milestone, Checkpoint, Project, User

from pydantic import BaseModel, Field

# ========== SCHEMAS ==========

class MilestoneCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class MilestoneResponse(BaseModel):
    milestone_id: int
    project_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    completed: bool
    checkpoints: List[dict] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class CheckpointCreate(BaseModel):
    milestone_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order: Optional[int] = 0

class CheckpointUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    order: Optional[int] = None

class CheckpointResponse(BaseModel):
    checkpoint_id: int
    milestone_id: int
    title: str
    description: Optional[str]
    completed: bool
    order: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== ROUTER ==========

router = APIRouter()


# ============ MILESTONES ============

@router.post("/", response_model=MilestoneResponse, status_code=201)
async def create_milestone(
    milestone_data: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo milestone mới cho project.
    Chỉ Lecturer (role_id=4) hoặc Admin mới có thể tạo.
    """
    if current_user.role_id not in [1, 4]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Lecturer mới có quyền tạo milestone"
        )
    
    # Kiểm tra project tồn tại
    project = await db.get(Project, milestone_data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project không tồn tại"
        )
    
    new_milestone = Milestone(
        project_id=milestone_data.project_id,
        title=milestone_data.title,
        description=milestone_data.description,
        due_date=milestone_data.due_date,
        completed=False
    )
    db.add(new_milestone)
    await db.commit()
    await db.refresh(new_milestone)
    
    return MilestoneResponse(
        milestone_id=new_milestone.milestone_id,
        project_id=new_milestone.project_id,
        title=new_milestone.title,
        description=new_milestone.description,
        due_date=new_milestone.due_date,
        completed=new_milestone.completed,
        checkpoints=[],
        created_at=new_milestone.created_at
    )


@router.get("/", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy danh sách milestones của project."""
    result = await db.execute(
        select(Milestone)
        .where(Milestone.project_id == project_id)
        .order_by(Milestone.due_date)
    )
    milestones = result.scalars().all()
    
    response = []
    for milestone in milestones:
        # Lấy checkpoints
        checkpoint_result = await db.execute(
            select(Checkpoint)
            .where(Checkpoint.milestone_id == milestone.milestone_id)
            .order_by(Checkpoint.order)
        )
        checkpoints = checkpoint_result.scalars().all()
        
        response.append(MilestoneResponse(
            milestone_id=milestone.milestone_id,
            project_id=milestone.project_id,
            title=milestone.title,
            description=milestone.description,
            due_date=milestone.due_date,
            completed=milestone.completed,
            checkpoints=[{
                "checkpoint_id": cp.checkpoint_id,
                "title": cp.title,
                "completed": cp.completed
            } for cp in checkpoints],
            created_at=milestone.created_at
        ))
    
    return response


@router.get("/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy chi tiết milestone."""
    milestone = await db.get(Milestone, milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone không tồn tại"
        )
    
    # Lấy checkpoints
    checkpoint_result = await db.execute(
        select(Checkpoint)
        .where(Checkpoint.milestone_id == milestone_id)
        .order_by(Checkpoint.order)
    )
    checkpoints = checkpoint_result.scalars().all()
    
    return MilestoneResponse(
        milestone_id=milestone.milestone_id,
        project_id=milestone.project_id,
        title=milestone.title,
        description=milestone.description,
        due_date=milestone.due_date,
        completed=milestone.completed,
        checkpoints=[{
            "checkpoint_id": cp.checkpoint_id,
            "title": cp.title,
            "completed": cp.completed,
            "description": cp.description
        } for cp in checkpoints],
        created_at=milestone.created_at
    )


@router.put("/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: int,
    update_data: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật milestone."""
    if current_user.role_id not in [1, 4]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Lecturer mới có quyền cập nhật milestone"
        )
    
    milestone = await db.get(Milestone, milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone không tồn tại"
        )
    
    if update_data.title is not None:
        milestone.title = update_data.title
    if update_data.description is not None:
        milestone.description = update_data.description
    if update_data.due_date is not None:
        milestone.due_date = update_data.due_date
    if update_data.completed is not None:
        milestone.completed = update_data.completed
    
    await db.commit()
    await db.refresh(milestone)
    
    return MilestoneResponse(
        milestone_id=milestone.milestone_id,
        project_id=milestone.project_id,
        title=milestone.title,
        description=milestone.description,
        due_date=milestone.due_date,
        completed=milestone.completed,
        checkpoints=[],
        created_at=milestone.created_at
    )


@router.delete("/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Xóa milestone (cascade xóa checkpoints)."""
    if current_user.role_id not in [1, 4]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Lecturer mới có quyền xóa milestone"
        )
    
    milestone = await db.get(Milestone, milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone không tồn tại"
        )
    
    await db.delete(milestone)
    await db.commit()
    return None


# ============ CHECKPOINTS ============

@router.post("/checkpoints/", response_model=CheckpointResponse, status_code=201)
async def create_checkpoint(
    checkpoint_data: CheckpointCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Tạo checkpoint mới."""
    milestone = await db.get(Milestone, checkpoint_data.milestone_id)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone không tồn tại"
        )
    
    new_checkpoint = Checkpoint(
        milestone_id=checkpoint_data.milestone_id,
        title=checkpoint_data.title,
        description=checkpoint_data.description,
        order=checkpoint_data.order,
        completed=False
    )
    db.add(new_checkpoint)
    await db.commit()
    await db.refresh(new_checkpoint)
    
    return CheckpointResponse(
        checkpoint_id=new_checkpoint.checkpoint_id,
        milestone_id=new_checkpoint.milestone_id,
        title=new_checkpoint.title,
        description=new_checkpoint.description,
        completed=new_checkpoint.completed,
        order=new_checkpoint.order,
        created_at=new_checkpoint.created_at
    )


@router.put("/checkpoints/{checkpoint_id}", response_model=CheckpointResponse)
async def update_checkpoint(
    checkpoint_id: int,
    update_data: CheckpointUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật checkpoint."""
    checkpoint = await db.get(Checkpoint, checkpoint_id)
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint không tồn tại"
        )
    
    if update_data.title is not None:
        checkpoint.title = update_data.title
    if update_data.description is not None:
        checkpoint.description = update_data.description
    if update_data.completed is not None:
        checkpoint.completed = update_data.completed
    if update_data.order is not None:
        checkpoint.order = update_data.order
    
    await db.commit()
    await db.refresh(checkpoint)
    
    return CheckpointResponse(
        checkpoint_id=checkpoint.checkpoint_id,
        milestone_id=checkpoint.milestone_id,
        title=checkpoint.title,
        description=checkpoint.description,
        completed=checkpoint.completed,
        order=checkpoint.order,
        created_at=checkpoint.created_at
    )


@router.delete("/checkpoints/{checkpoint_id}", status_code=204)
async def delete_checkpoint(
    checkpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Xóa checkpoint."""
    checkpoint = await db.get(Checkpoint, checkpoint_id)
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint không tồn tại"
        )
    
    await db.delete(checkpoint)
    await db.commit()
    return None
