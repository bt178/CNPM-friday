"""
BE2 - Topics & Evaluation Endpoints
Starter template - Just copy and modify!
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from uuid import UUID

from app.api import deps
from app.models.all_models import Topic, User, Evaluation, EvaluationDetail
from app.schemas import user as user_schema  # Reuse existing

router = APIRouter()

# ===== SCHEMAS (Add to app/schemas/topic.py) =====
# from pydantic import BaseModel
# from typing import Optional
# 
# class TopicCreate(BaseModel):
#     title: str
#     description: Optional[str] = None
#     requirements: Optional[str] = None
#
# class TopicUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     status: Optional[str] = None


# ===== ENDPOINTS =====

@router.post("/topics", tags=["topics"])
async def create_topic(
    title: str,
    description: str = "",
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Lecturer creates a new topic
    Only ADMIN (1) and LECTURER (4) can create
    """
    if current_user.role_id not in [1, 4]:
        raise HTTPException(status_code=403, detail="Only lecturers can create topics")
    
    topic = Topic(
        title=title,
        description=description,
        created_by=current_user.user_id,
        status="DRAFT",
        created_at=datetime.now(timezone.utc)
    )
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return {
        "topic_id": topic.topic_id,
        "title": topic.title,
        "status": topic.status,
        "created_by": str(topic.created_by)
    }


@router.get("/topics", tags=["topics"])
async def list_topics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List topics
    - Students see only APPROVED topics
    - Lecturers/Admin see all
    """
    query = select(Topic)
    
    # Filter by role
    if current_user.role_id == 5:  # Student
        query = query.where(Topic.status == "APPROVED")
    
    result = await db.execute(query)
    topics = result.scalars().all()
    
    return [
        {
            "topic_id": t.topic_id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "created_by": str(t.created_by),
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in topics
    ]


@router.get("/topics/{topic_id}", tags=["topics"])
async def get_topic_detail(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get detailed topic info"""
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Student can only see APPROVED
    if current_user.role_id == 5 and topic.status != "APPROVED":
        raise HTTPException(status_code=403, detail="Cannot view this topic")
    
    return {
        "topic_id": topic.topic_id,
        "title": topic.title,
        "description": topic.description,
        "status": topic.status,
        "created_by": str(topic.created_by),
        "created_at": topic.created_at.isoformat() if topic.created_at else None,
        "approved_by": str(topic.approved_by) if topic.approved_by else None,
        "approved_at": topic.approved_at.isoformat() if topic.approved_at else None,
    }


@router.patch("/topics/{topic_id}/approve", tags=["topics"])
async def approve_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Approve a topic
    Only HEAD_DEPT (3) or ADMIN (1) can approve
    """
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Only admins/department heads can approve")
    
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if topic.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Topic must be in DRAFT status")
    
    topic.status = "APPROVED"
    topic.approved_by = current_user.user_id
    topic.approved_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(topic)
    
    return {
        "topic_id": topic.topic_id,
        "status": topic.status,
        "approved_by": str(topic.approved_by),
        "message": "Topic approved successfully"
    }


@router.patch("/topics/{topic_id}/reject", tags=["topics"])
async def reject_topic(
    topic_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Reject and return to DRAFT status"""
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="Only admins/department heads can reject")
    
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    topic.status = "DRAFT"
    topic.approved_by = None
    topic.approved_at = None
    
    await db.commit()
    return {"topic_id": topic.topic_id, "status": "DRAFT", "message": "Topic rejected"}


@router.post("/evaluations", tags=["evaluation"])
async def create_evaluation(
    team_id: int,
    project_id: int,
    score: float,
    feedback: str = "",
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Lecturer evaluates a team
    Only LECTURER (4) or ADMIN (1) can evaluate
    """
    if current_user.role_id not in [1, 4]:
        raise HTTPException(status_code=403, detail="Only lecturers can evaluate")
    
    evaluation = Evaluation(
        team_id=team_id,
        project_id=project_id,
        evaluated_by=current_user.user_id,
        score=score,
        feedback=feedback,
        created_at=datetime.now(timezone.utc)
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    
    return {
        "evaluation_id": evaluation.evaluation_id,
        "team_id": team_id,
        "score": score,
        "evaluated_by": str(current_user.user_id),
        "created_at": evaluation.created_at.isoformat()
    }


@router.get("/evaluations/{evaluation_id}", tags=["evaluation"])
async def get_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get evaluation details"""
    evaluation = await db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return {
        "evaluation_id": evaluation.evaluation_id,
        "team_id": evaluation.team_id,
        "project_id": evaluation.project_id,
        "score": evaluation.score,
        "feedback": evaluation.feedback,
        "evaluated_by": str(evaluation.evaluated_by),
        "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None,
    }
