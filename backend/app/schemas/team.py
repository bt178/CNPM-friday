"""
Pydantic schemas for Team and TeamMember management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ==========================================
# TEAM SCHEMAS
# ==========================================

class TeamBase(BaseModel):
    """Base schema for Team."""
    team_name: Optional[str] = Field(None, max_length=255)


class TeamCreate(TeamBase):
    """Schema for creating a new Team."""
    class_id: int
    project_id: Optional[int] = Field(None, description="Optional: Link to project immediately")
    # leader_id will be taken from JWT token (current student)


class TeamUpdate(BaseModel):
    """Schema for updating Team."""
    team_name: Optional[str] = None
    project_id: Optional[int] = Field(None, description="Assign or change project")


class TeamResponse(TeamBase):
    """Schema for Team response."""
    team_id: int
    project_id: Optional[int]
    leader_id: UUID
    class_id: int
    join_code: Optional[str]
    created_at: datetime

    # Nested info
    leader_name: Optional[str] = None
    class_code: Optional[str] = None
    project_name: Optional[str] = None
    member_count: int = 0

    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    """Detailed Team response with members list."""
    members: list["TeamMemberResponse"] = []

    class Config:
        from_attributes = True


# ==========================================
# TEAM MEMBER SCHEMAS
# ==========================================

class TeamMemberBase(BaseModel):
    """Base schema for TeamMember."""
    role: Optional[str] = Field(None, max_length=100, description="e.g., Developer, Designer, QA")


class TeamMemberCreate(TeamMemberBase):
    """Schema for adding a member to team."""
    student_id: UUID


class TeamMemberUpdate(BaseModel):
    """Schema for updating team member."""
    role: Optional[str] = None
    is_active: Optional[bool] = None


class TeamMemberResponse(TeamMemberBase):
    """Schema for TeamMember response."""
    team_id: int
    student_id: UUID
    is_active: bool
    joined_at: datetime

    # Student info
    student_name: Optional[str] = None
    student_email: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# TEAM INVITATION SCHEMAS
# ==========================================

class TeamJoinRequest(BaseModel):
    """Schema for student joining team via code."""
    join_code: str = Field(..., min_length=6, max_length=20)


class TeamInviteRequest(BaseModel):
    """Schema for leader inviting student by email."""
    student_email: str = Field(..., description="Email of student to invite")
    role: Optional[str] = Field(None, description="Assigned role in team")


class TeamRemoveMemberRequest(BaseModel):
    """Schema for removing a team member."""
    student_id: UUID


# ==========================================
# LECTURER TEAM MANAGEMENT
# ==========================================

class TeamLockRequest(BaseModel):
    """Schema for lecturer to finalize/lock a team."""
    is_locked: bool = Field(..., description="True to lock, False to unlock")
    lock_reason: Optional[str] = Field(None, description="Reason for locking")


class TeamAssignProjectRequest(BaseModel):
    """Schema for lecturer to assign project to team."""
    project_id: int