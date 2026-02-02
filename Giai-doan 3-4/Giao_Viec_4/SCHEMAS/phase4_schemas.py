# Pydantic Schemas cho Phase 4: Mentoring, Peer Reviews, Milestones, Submissions, Resources

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum


# ==========================================
# MENTORING SCHEMAS
# ==========================================

class MentoringLogCreate(BaseModel):
    """Schema để tạo mentoring log"""
    team_id: int = Field(..., description="ID của team")
    content: str = Field(..., min_length=1, description="Nội dung buổi mentoring")
    meeting_date: Optional[datetime] = Field(None, description="Ngày họp mentoring")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": 1,
                "content": "Discussed project architecture and sprint planning",
                "meeting_date": "2026-02-15T14:00:00Z"
            }
        }


class MentoringLogResponse(BaseModel):
    """Schema response cho mentoring log"""
    log_id: int
    team_id: int
    lecturer_id: UUID
    lecturer_name: Optional[str] = None
    content: Optional[str]
    meeting_date: Optional[datetime]
    ai_suggestions: Optional[str]  # AI-generated recommendations
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AISuggestionRequest(BaseModel):
    """Schema để yêu cầu AI suggestions"""
    team_id: int = Field(..., description="ID của team cần analyze")
    include_peer_reviews: bool = Field(True, description="Có phân tích peer reviews không")
    include_task_progress: bool = Field(True, description="Có phân tích task progress không")


class AISuggestionResponse(BaseModel):
    """Schema response cho AI suggestions"""
    team_id: int
    suggestions: List[str]
    analysis_summary: str
    generated_at: datetime


# ==========================================
# PEER REVIEW SCHEMAS
# ==========================================

class PeerReviewCreate(BaseModel):
    """Schema để tạo peer review"""
    team_id: int = Field(..., description="ID của team")
    reviewee_id: UUID = Field(..., description="ID của người được review")
    sprint_id: Optional[int] = Field(None, description="ID của sprint (nếu có)")
    criteria_name: str = Field(..., description="Tiêu chí đánh giá: collaboration, communication, contribution")
    score: int = Field(..., ge=1, le=5, description="Điểm từ 1-5")
    comment: Optional[str] = Field(None, max_length=1000, description="Nhận xét (tùy chọn)")

    @validator('score')
    def validate_score(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Score must be between 1 and 5')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": 1,
                "reviewee_id": "123e4567-e89b-12d3-a456-426614174000",
                "sprint_id": 1,
                "criteria_name": "collaboration",
                "score": 4,
                "comment": "Great teamwork!"
            }
        }


class PeerReviewResponse(BaseModel):
    """Schema response cho peer review (KHÔNG có reviewer_id để đảm bảo anonymous)"""
    review_id: int
    team_id: int
    # NOTE: KHÔNG bao gồm reviewer_id để đảm bảo anonymous!
    reviewee_id: UUID
    reviewee_name: Optional[str] = None
    sprint_id: Optional[int] = None
    criteria_name: Optional[str]
    score: Optional[int]
    comment: Optional[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PeerReviewSummary(BaseModel):
    """Schema tổng hợp peer reviews cho một người"""
    user_id: UUID
    user_name: str
    average_score: float
    review_count: int
    by_criteria: dict  # {"collaboration": 4.2, "communication": 3.8, ...}


# ==========================================
# MILESTONE SCHEMAS
# ==========================================

class MilestoneCreate(BaseModel):
    """Schema để tạo milestone"""
    class_id: int = Field(..., description="ID của academic class")
    title: str = Field(..., min_length=1, max_length=200, description="Tiêu đề milestone")
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    due_date: datetime = Field(..., description="Deadline")

    class Config:
        json_schema_extra = {
            "example": {
                "class_id": 1,
                "title": "Sprint 1 Review",
                "description": "Submit Sprint 1 deliverables",
                "due_date": "2026-02-20T23:59:59Z"
            }
        }


class MilestoneUpdate(BaseModel):
    """Schema để cập nhật milestone"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class MilestoneResponse(BaseModel):
    """Schema response cho milestone"""
    milestone_id: int
    class_id: int
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[datetime]
    created_by: UUID
    creator_name: Optional[str] = None
    checkpoint_count: int = 0

    class Config:
        from_attributes = True


# ==========================================
# CHECKPOINT SCHEMAS
# ==========================================

class CheckpointCreate(BaseModel):
    """Schema để tạo checkpoint cho team trong milestone"""
    team_id: int = Field(..., description="ID của team")
    milestone_id: int = Field(..., description="ID của milestone")
    title: str = Field(..., min_length=1, max_length=200, description="Tiêu đề checkpoint")
    status: Optional[str] = Field("pending", description="Trạng thái: pending, in_progress, submitted, graded")


class CheckpointResponse(BaseModel):
    """Schema response cho checkpoint"""
    checkpoint_id: int
    team_id: int
    milestone_id: int
    title: Optional[str]
    status: Optional[str]
    submission_count: int = 0

    class Config:
        from_attributes = True


# ==========================================
# SUBMISSION SCHEMAS
# ==========================================

class SubmissionCreate(BaseModel):
    """Schema để tạo submission"""
    checkpoint_id: int = Field(..., description="ID của checkpoint")
    content: str = Field(..., min_length=1, description="Nội dung submission")
    file_url: Optional[str] = Field(None, description="URL file đính kèm (nếu có)")

    class Config:
        json_schema_extra = {
            "example": {
                "checkpoint_id": 1,
                "content": "Sprint 1 completed with all user stories delivered",
                "file_url": "https://storage.example.com/submissions/sprint1.pdf"
            }
        }


class SubmissionUpdate(BaseModel):
    """Schema để cập nhật submission (chỉ trước deadline)"""
    content: Optional[str] = Field(None, min_length=1)
    file_url: Optional[str] = None


class SubmissionGrade(BaseModel):
    """Schema để chấm điểm submission (lecturer only)"""
    score: float = Field(..., ge=0, le=10, description="Điểm từ 0-10")
    feedback: Optional[str] = Field(None, description="Nhận xét của giảng viên")


class SubmissionResponse(BaseModel):
    """Schema response cho submission"""
    submission_id: int
    checkpoint_id: int
    submitted_by: UUID
    submitter_name: Optional[str] = None
    content: Optional[str]
    file_url: Optional[str]
    submitted_at: datetime
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# RESOURCE SCHEMAS
# ==========================================

class ResourceType(str, Enum):
    """Loại resource"""
    LINK = "link"
    FILE = "file"
    DOCUMENT = "document"
    VIDEO = "video"
    IMAGE = "image"


class ResourceCreate(BaseModel):
    """Schema để tạo resource"""
    team_id: Optional[int] = Field(None, description="ID của team (nếu resource cho team)")
    class_id: Optional[int] = Field(None, description="ID của class (nếu resource cho class)")
    file_url: str = Field(..., description="URL của resource")
    file_type: Optional[str] = Field("link", description="Loại: link, file, document, video, image")
    title: Optional[str] = Field(None, max_length=200, description="Tiêu đề resource")
    description: Optional[str] = Field(None, description="Mô tả")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": 1,
                "file_url": "https://docs.google.com/document/d/abc123",
                "file_type": "document",
                "title": "Project Requirements",
                "description": "Detailed project requirements document"
            }
        }


class ResourceResponse(BaseModel):
    """Schema response cho resource"""
    resource_id: int
    uploaded_by: UUID
    uploader_name: Optional[str] = None
    team_id: Optional[int]
    class_id: Optional[int]
    file_url: Optional[str]
    file_type: Optional[str]
    title: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# EVALUATION DETAIL SCHEMAS (bổ sung cho Phase 4)
# ==========================================

class EvaluationDetailCreate(BaseModel):
    """Schema để thêm chi tiết đánh giá theo tiêu chí"""
    evaluation_id: int = Field(..., description="ID của evaluation")
    criteria_id: int = Field(..., description="ID của tiêu chí đánh giá")
    score: float = Field(..., ge=0, description="Điểm")
    comment: Optional[str] = Field(None, description="Nhận xét")


class EvaluationDetailResponse(BaseModel):
    """Schema response cho chi tiết đánh giá"""
    detail_id: int
    evaluation_id: int
    criteria_id: int
    criteria_name: Optional[str] = None
    score: Optional[float]
    comment: Optional[str]

    class Config:
        from_attributes = True


class EvaluationSummary(BaseModel):
    """Schema tổng hợp đánh giá"""
    evaluation_id: int
    total_score: float
    max_score: float
    percentage: float
    details: List[EvaluationDetailResponse]
