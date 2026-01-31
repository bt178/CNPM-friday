"""Topic schemas for request/response validation."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None

class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None

class TopicResponse(BaseModel):
    topic_id: int
    title: str
    description: Optional[str]
    status: str
    created_by: str
    created_at: Optional[datetime]
    approved_by: Optional[str]
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True

class EvaluationCreate(BaseModel):
    team_id: int
    project_id: int
    score: float
    feedback: Optional[str] = None
