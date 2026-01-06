"""
Pydantic schemas for Task Board (Kanban-style) and Sprint management.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==========================================
# SPRINT SCHEMAS
# ==========================================

class SprintBase(BaseModel):
    """Base schema for Sprint."""
    title: Optional[str] = Field(None, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class SprintCreate(SprintBase):
    """Schema for creating a Sprint."""
    team_id: int


class SprintUpdate(BaseModel):
    """Schema for updating Sprint."""
    title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, description="planned, active, completed")


class SprintResponse(SprintBase):
    """Schema for Sprint response."""
    sprint_id: int
    team_id: int
    status: Optional[str]
    task_count: int = 0

    class Config:
        from_attributes = True


# ==========================================
# TASK SCHEMAS
# ==========================================

class TaskBase(BaseModel):
    """Base schema for Task."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field("medium", description="low, medium, high")


class TaskCreate(TaskBase):
    """Schema for creating a Task."""
    sprint_id: Optional[int] = Field(None, description="Sprint ID (can be null for backlog)")
    assignee_id: Optional[UUID] = Field(None, description="Assigned team member")
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema for updating Task."""
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[UUID] = None
    priority: Optional[str] = Field(None, description="low, medium, high")
    status: Optional[str] = Field(None, description="todo, doing, done")
    sprint_id: Optional[int] = Field(None, description="Move to different sprint")
    due_date: Optional[datetime] = None


class TaskStatusUpdate(BaseModel):
    """Schema for quick status update (drag & drop)."""
    status: str = Field(..., description="todo, doing, done")


class TaskResponse(TaskBase):
    """Schema for Task response."""
    task_id: int
    sprint_id: Optional[int]
    assignee_id: Optional[UUID]
    status: Optional[str]
    created_at: datetime
    due_date: Optional[datetime]

    # Nested info
    assignee_name: Optional[str] = None
    sprint_title: Optional[str] = None

    class Config:
        from_attributes = True


class TaskBoardResponse(BaseModel):
    """Schema for Task Board grouped by status (Kanban view)."""
    todo: list[TaskResponse] = []
    doing: list[TaskResponse] = []
    done: list[TaskResponse] = []
    backlog: list[TaskResponse] = []  # Tasks without sprint


class TaskStatistics(BaseModel):
    """Schema for Task statistics."""
    total_tasks: int
    todo_count: int
    doing_count: int
    done_count: int
    completion_rate: float = Field(0.0, description="Percentage of done tasks")