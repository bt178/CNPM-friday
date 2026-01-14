"""
FastAPI endpoints for Topic (Project Proposal) management.
Ticket: BE-PROJ-01

Status Workflow: draft → pending → approved (or rejected)
- Lecturer creates topics (status=draft)
- Lecturer submits for approval (draft→pending)
- Head of Department approves/rejects (pending→approved/rejected)
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.all_models import Topic, User
from app.schemas.project import TopicCreate, TopicUpdate, TopicResponse, TopicListResponse

router = APIRouter()


# ==========================================
# TOPIC CRUD ENDPOINTS
# ==========================================

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new Topic (Project Proposal).
    Only Lecturers can create topics.
    Initial status is 'draft'.
    """
    # Check if user is a lecturer
    if current_user.role.role_name.upper() != "LECTURER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can create topics"
        )
    
    # Create topic with creator_id from JWT
    topic = Topic(
        title=topic_in.title,
        description=topic_in.description,
        objectives=topic_in.objectives,
        tech_stack=topic_in.tech_stack,
        dept_id=topic_in.dept_id,
        creator_id=current_user.user_id,
        status="draft",
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    
    # Build response with creator name
    return TopicResponse(
        topic_id=topic.topic_id,
        title=topic.title,
        description=topic.description,
        objectives=topic.objectives,
        tech_stack=topic.tech_stack,
        creator_id=topic.creator_id,
        dept_id=topic.dept_id,
        status=topic.status or "draft",
        created_at=topic.created_at,
        creator_name=current_user.full_name,
    )


@router.get("/", response_model=TopicListResponse)
async def list_topics(
    dept_id: Optional[int] = Query(None, description="Filter by department"),
    status: Optional[str] = Query(None, description="Filter by status: draft, pending, approved, rejected"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    List all topics with optional filters.
    - Lecturers can see their own topics (all statuses)
    - Students can only see 'approved' topics
    - Head of Department can see all topics in their department
    """
    query = select(Topic).options(selectinload(Topic.creator))
    
    # Apply role-based filtering
    user_role = current_user.role.role_name.upper()
    
    if user_role == "STUDENT":
        # Students can only see approved topics
        query = query.where(Topic.status == "approved")
    elif user_role == "LECTURER":
        # Lecturers see their own topics or approved topics
        query = query.where(
            (Topic.creator_id == current_user.user_id) | (Topic.status == "approved")
        )
    elif user_role == "HEAD_DEPT":
        # Head of dept sees all in their department
        if current_user.dept_id:
            query = query.where(Topic.dept_id == current_user.dept_id)
    # ADMIN can see all
    
    # Apply filters
    if dept_id is not None:
        query = query.where(Topic.dept_id == dept_id)
    if status is not None:
        query = query.where(Topic.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Topic.created_at.desc())
    
    result = await db.execute(query)
    topics = result.scalars().all()
    
    # Build response
    items = []
    for topic in topics:
        items.append(TopicResponse(
            topic_id=topic.topic_id,
            title=topic.title,
            description=topic.description,
            objectives=topic.objectives,
            tech_stack=topic.tech_stack,
            creator_id=topic.creator_id,
            dept_id=topic.dept_id,
            status=topic.status or "draft",
            created_at=topic.created_at,
            creator_name=topic.creator.full_name if topic.creator else None,
        ))
    
    return TopicListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get topic details by ID."""
    result = await db.execute(
        select(Topic)
        .options(selectinload(Topic.creator))
        .where(Topic.topic_id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check access rights
    user_role = current_user.role.role_name.upper()
    if user_role == "STUDENT" and topic.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view approved topics"
        )
    
    return TopicResponse(
        topic_id=topic.topic_id,
        title=topic.title,
        description=topic.description,
        objectives=topic.objectives,
        tech_stack=topic.tech_stack,
        creator_id=topic.creator_id,
        dept_id=topic.dept_id,
        status=topic.status or "draft",
        created_at=topic.created_at,
        creator_name=topic.creator.full_name if topic.creator else None,
    )


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a topic.
    Only the creator (lecturer) can update their own topics.
    Cannot update after topic is approved.
    """
    result = await db.execute(
        select(Topic)
        .options(selectinload(Topic.creator))
        .where(Topic.topic_id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check ownership
    if topic.creator_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own topics"
        )
    
    # Cannot update approved topics
    if topic.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update approved topics"
        )
    
    # Update fields
    update_data = topic_in.model_dump(exclude_unset=True)
    # Don't allow status change via update endpoint
    update_data.pop("status", None)
    
    for field, value in update_data.items():
        setattr(topic, field, value)
    
    await db.commit()
    await db.refresh(topic)
    
    return TopicResponse(
        topic_id=topic.topic_id,
        title=topic.title,
        description=topic.description,
        objectives=topic.objectives,
        tech_stack=topic.tech_stack,
        creator_id=topic.creator_id,
        dept_id=topic.dept_id,
        status=topic.status or "draft",
        created_at=topic.created_at,
        creator_name=topic.creator.full_name if topic.creator else None,
    )


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a topic.
    Only the creator can delete their own draft/rejected topics.
    Cannot delete approved/pending topics.
    """
    result = await db.execute(
        select(Topic).where(Topic.topic_id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check ownership
    if topic.creator_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own topics"
        )
    
    # Cannot delete approved or pending topics
    if topic.status in ("approved", "pending"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete topics with status '{topic.status}'"
        )
    
    await db.delete(topic)
    await db.commit()
    return None


# ==========================================
# STATUS WORKFLOW ENDPOINTS
# ==========================================

@router.post("/{topic_id}/submit", response_model=TopicResponse)
async def submit_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Submit topic for approval (draft → pending).
    Only the creator can submit their own topics.
    """
    result = await db.execute(
        select(Topic)
        .options(selectinload(Topic.creator))
        .where(Topic.topic_id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check ownership
    if topic.creator_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own topics"
        )
    
    # Check current status
    if topic.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only draft topics can be submitted. Current status: {topic.status}"
        )
    
    # Update status
    topic.status = "pending"
    await db.commit()
    await db.refresh(topic)
    
    return TopicResponse(
        topic_id=topic.topic_id,
        title=topic.title,
        description=topic.description,
        objectives=topic.objectives,
        tech_stack=topic.tech_stack,
        creator_id=topic.creator_id,
        dept_id=topic.dept_id,
        status=topic.status,
        created_at=topic.created_at,
        creator_name=topic.creator.full_name if topic.creator else None,
    )


@router.post("/{topic_id}/approve", response_model=TopicResponse)
async def approve_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Approve a topic (pending → approved).
    Only HEAD_DEPT or ADMIN can approve topics.
    """
    # Check role
    user_role = current_user.role.role_name.upper()
    if user_role not in ("HEAD_DEPT", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Head of Department or Admin can approve topics"
        )
    
    result = await db.execute(
        select(Topic)
        .options(selectinload(Topic.creator))
        .where(Topic.topic_id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check current status
    if topic.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only pending topics can be approved. Current status: {topic.status}"
        )
    
    # Update status
    topic.status = "approved"
    await db.commit()
    await db.refresh(topic)
    
    return TopicResponse(
        topic_id=topic.topic_id,
        title=topic.title,
        description=topic.description,
        objectives=topic.objectives,
        tech_stack=topic.tech_stack,
        creator_id=topic.creator_id,
        dept_id=topic.dept_id,
        status=topic.status,
        created_at=topic.created_at,
        creator_name=topic.creator.full_name if topic.creator else None,
    )


@router.post("/{topic_id}/reject", response_model=TopicResponse)
async def reject_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Reject a topic (pending → rejected).
    Only HEAD_DEPT or ADMIN can reject topics.
    """
    # Check role
    user_role = current_user.role.role_name.upper()
    if user_role not in ("HEAD_DEPT", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Head of Department or Admin can reject topics"
        )
    
    result = await db.execute(
        select(Topic)
        .options(selectinload(Topic.creator))
        .where(Topic.topic_id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Check current status
    if topic.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only pending topics can be rejected. Current status: {topic.status}"
        )
    
    # Update status
    topic.status = "rejected"
    await db.commit()
    await db.refresh(topic)
    
    return TopicResponse(
        topic_id=topic.topic_id,
        title=topic.title,
        description=topic.description,
        objectives=topic.objectives,
        tech_stack=topic.tech_stack,
        creator_id=topic.creator_id,
        dept_id=topic.dept_id,
        status=topic.status,
        created_at=topic.created_at,
        creator_name=topic.creator.full_name if topic.creator else None,
    )
