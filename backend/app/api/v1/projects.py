"""
FastAPI endpoints for Project management.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.all_models import Project, Topic, Team, User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    TopicResponse,
)

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Project linking a Topic to an Academic Class.
    Only Lecturers can create projects.
    """
    # Role check
    if current_user.role_id != 4: # Lecturer
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can create projects"
        )
    
    # Verify topic exists and is approved (Case-insensitive check)
    topic_result = await db.execute(
        select(Topic).where(Topic.topic_id == payload.topic_id)
    )
    topic = topic_result.scalar_one_or_none()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    if topic.status and topic.status.upper() != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only create projects from approved topics. Current: {topic.status}"
        )
    
    project = Project(
        project_name=payload.project_name,
        topic_id=payload.topic_id,
        class_id=payload.class_id,
        status="active",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    class_id: Optional[int] = Query(None, description="Filter by class"),
    topic_id: Optional[int] = Query(None, description="Filter by topic"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all projects.
    """
    query = select(Project)
    
    if class_id is not None:
        query = query.where(Project.class_id == class_id)
    
    if topic_id is not None:
        query = query.where(Project.topic_id == topic_id)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project details."""
    result = await db.execute(
        select(Project)
        .where(Project.project_id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project
