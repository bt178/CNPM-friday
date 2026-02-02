from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.all_models import User, Topic, Evaluation
from app.schemas.topic import (
    TopicCreate, TopicUpdate, TopicResponse, EvaluationCreate, EvaluationResponse
)
from app.dao.topic_dao import TopicDAO

router = APIRouter()

# ============================================================================
# TOPICS ENDPOINTS
# ============================================================================

@router.post("", status_code=201)
async def create_topic(
    topic: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new topic (Lecturer only)
    """
    if current_user.role_id != 4:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can create topics"
        )
    
    dao = TopicDAO(db)
    new_topic = await dao.create_topic(topic, current_user.user_id)
    
    return {
        "topic_id": new_topic.topic_id,
        "title": new_topic.title,
        "description": new_topic.description,
        "requirements": new_topic.requirements,
        "objectives": new_topic.objectives,
        "tech_stack": new_topic.tech_stack,
        "status": new_topic.status,
        "created_by": current_user.full_name,
        "creator_id": new_topic.creator_id,
        "created_at": new_topic.created_at
    }

@router.get("")
async def get_topics(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get topics list with caching and relationships optimized via DAO
    """
    dao = TopicDAO(db)
    
    filter_status = status_filter
    if current_user.role_id == 5: # Student
        filter_status = "APPROVED"
        if status_filter and status_filter != "APPROVED":
             return {"topics": [], "total": 0}

    topics = await dao.get_all_topics(status=filter_status)
    
    topics_response = []
    for t in topics:
        topics_response.append({
            "topic_id": t.topic_id,
            "title": t.title,
            "description": t.description,
            "requirements": t.requirements,
            "objectives": t.objectives,
            "tech_stack": t.tech_stack,
            "status": t.status,
            "created_by": t.creator.full_name if t.creator else "Unknown",
            "creator_id": t.creator_id,
            "dept_id": t.dept_id,
            "created_at": t.created_at
        })
    
    return {
        "topics": topics_response,
        "total": len(topics_response)
    }

@router.get("/{topic_id}")
async def get_topic_detail(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get topic details by ID
    """
    dao = TopicDAO(db)
    topic = await dao.get_topic_by_id(topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    if current_user.role_id == 5 and topic.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view approved topics"
        )
    
    approver_name = None
    if topic.approved_by:
        approver_query = select(User).where(User.user_id == topic.approved_by)
        approver_result = await db.execute(approver_query)
        approver = approver_result.scalar()
        if approver:
            approver_name = approver.full_name
            
    return {
        "topic_id": topic.topic_id,
        "title": topic.title,
        "description": topic.description,
        "requirements": topic.requirements,
        "objectives": topic.objectives,
        "tech_stack": topic.tech_stack,
        "status": topic.status,
        "created_by": topic.creator.full_name if topic.creator else "Unknown",
        "creator_id": topic.creator_id,
        "dept_id": topic.dept_id,
        "created_at": topic.created_at,
        "approved_by": approver_name,
        "approved_at": topic.approved_at
    }

@router.patch("/{topic_id}/approve")
async def approve_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a topic (HEAD_DEPT or ADMIN only)
    """
    if current_user.role_id not in [1, 3]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or heads of department can approve topics"
        )
    
    dao = TopicDAO(db)
    query = select(Topic).where(Topic.topic_id == topic_id)
    result = await db.execute(query)
    topic = result.scalar()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    updated_topic = await dao.update_topic_status(topic, "APPROVED", current_user.user_id)
    
    return {
        "topic_id": updated_topic.topic_id,
        "status": updated_topic.status,
        "approved_by": current_user.full_name,
        "approved_at": updated_topic.approved_at
    }

@router.patch("/{topic_id}/reject")
async def reject_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a topic (HEAD_DEPT or ADMIN only)
    """
    if current_user.role_id not in [1, 3]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or heads of department can reject topics"
        )
    
    dao = TopicDAO(db)
    query = select(Topic).where(Topic.topic_id == topic_id)
    result = await db.execute(query)
    topic = result.scalar()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    updated_topic = await dao.update_topic_status(topic, "REJECTED", current_user.user_id)
    
    return {
        "topic_id": updated_topic.topic_id,
        "status": updated_topic.status,
        "rejected_by": current_user.full_name,
        "rejected_at": updated_topic.approved_at
    }

# ============================================================================
# EVALUATION ENDPOINTS
# ============================================================================

@router.post("/{topic_id}/evaluate", response_model=EvaluationResponse)
async def create_evaluation(
    topic_id: int,
    eval_data: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create evaluation for a team on a topic (Lecturer only)
    """
    if current_user.role_id != 4:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can create evaluations"
        )
    
    topic_query = select(Topic).where(Topic.topic_id == topic_id)
    topic_result = await db.execute(topic_query)
    topic = topic_result.scalar()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    evaluation = Evaluation(
        team_id=eval_data.team_id,
        topic_id=topic_id,
        evaluator_id=current_user.user_id,
        score=eval_data.score,
        feedback=eval_data.feedback,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    
    return {
        "evaluation_id": evaluation.evaluation_id,
        "team_id": evaluation.team_id,
        "topic_id": evaluation.topic_id,
        "score": evaluation.score,
        "feedback": evaluation.feedback,
        "evaluator": current_user.full_name,
        "created_at": evaluation.created_at
    }
