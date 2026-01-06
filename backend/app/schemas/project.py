"""
Pydantic schemas for Project and Topic (Project Proposal) management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==========================================
# TOPIC (PROJECT PROPOSAL) SCHEMAS
# ==========================================

class TopicBase(BaseModel):
    """Base schema for Topic with common fields."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    objectives: Optional[str] = None
    tech_stack: Optional[str] = Field(None, description="Comma-separated tech stack")


class TopicCreate(TopicBase):
    """Schema for creating a new Topic (Lecturer only)."""
    dept_id: int = Field(..., description="Department ID")
    # creator_id will be taken from JWT token, not from request body


class TopicUpdate(BaseModel):
    """Schema for updating an existing Topic."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    objectives: Optional[str] = None
    tech_stack: Optional[str] = None
    status: Optional[str] = Field(None, description="draft, pending, approved, rejected")


class TopicResponse(TopicBase):
    """Schema for Topic response."""
    topic_id: int
    creator_id: UUID
    dept_id: int
    status: str = Field(default="draft")
    created_at: datetime

    # Include creator info
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True


class TopicListResponse(BaseModel):
    """Schema for paginated Topic list."""
    items: list[TopicResponse]
    total: int
    page: int
    page_size: int


# ==========================================
# PROJECT SCHEMAS
# ==========================================

class ProjectBase(BaseModel):
    """Base schema for Project."""
    project_name: Optional[str] = Field(None, max_length=255)


class ProjectCreate(ProjectBase):
    """Schema for creating a Project (linking Topic to Class)."""
    topic_id: int
    class_id: int


class ProjectUpdate(BaseModel):
    """Schema for updating Project."""
    project_name: Optional[str] = None
    status: Optional[str] = Field(None, description="active, completed, archived")


class ProjectResponse(ProjectBase):
    """Schema for Project response."""
    project_id: int
    topic_id: int
    class_id: int
    status: Optional[str]

    # Nested info
    topic_title: Optional[str] = None
    class_code: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Detailed Project response including topic details."""
    topic: Optional[TopicResponse] = None
    team_count: int = 0
    has_assigned_team: bool = False

    class Config:
        from_attributes = True