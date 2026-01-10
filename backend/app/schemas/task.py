"""Pydantic schemas for Task."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class TaskStatus(str, Enum):
    """Task status enum."""
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"


class TaskPriority(str, Enum):
    """Task priority enum."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ==================== TASK SCHEMAS ====================

class TaskBase(BaseModel):
    """Base schema for Task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """Schema for creating a Task."""
    title: str
    team_id: Optional[int] = None  # FIX: Made optional since model allows nullable
    sprint_id: Optional[int] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema for updating a Task."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[datetime] = None
    
    # FIX BUG-09: Add case-insensitive validator for status
    @field_validator('status', mode='before')
    @classmethod
    def convert_status_to_uppercase(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v
    
    @field_validator('priority', mode='before')
    @classmethod
    def convert_priority_to_uppercase(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v


class TaskResponse(TaskBase):
    """Schema for Task response."""
    task_id: int
    team_id: Optional[int] = None  # FIX: Made optional
    sprint_id: Optional[int] = None
    assignee_id: Optional[UUID] = None
    status: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True
