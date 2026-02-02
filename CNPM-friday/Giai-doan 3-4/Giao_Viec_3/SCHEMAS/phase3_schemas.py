# Pydantic Schemas cho Phase 3: Channels, Messages, Meetings

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# ==========================================
# CHANNEL SCHEMAS
# ==========================================

class ChannelCreate(BaseModel):
    """Schema để tạo channel mới trong team"""
    team_id: int = Field(..., description="ID của team sở hữu channel")
    name: str = Field(..., min_length=1, max_length=100, description="Tên channel")
    type: Optional[str] = Field("general", description="Loại channel: general, announcement, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": 1,
                "name": "general",
                "type": "general"
            }
        }


class ChannelUpdate(BaseModel):
    """Schema để cập nhật channel"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[str] = None


class ChannelResponse(BaseModel):
    """Schema response cho channel"""
    channel_id: int
    team_id: int
    name: Optional[str]
    type: Optional[str]
    created_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ==========================================
# MESSAGE SCHEMAS
# ==========================================

class MessageCreate(BaseModel):
    """Schema để gửi message mới"""
    channel_id: int = Field(..., description="ID của channel")
    content: str = Field(..., min_length=1, max_length=5000, description="Nội dung tin nhắn")
    reply_to_id: Optional[int] = Field(None, description="ID tin nhắn đang reply (nếu có)")

    class Config:
        json_schema_extra = {
            "example": {
                "channel_id": 1,
                "content": "Hello team!",
                "reply_to_id": None
            }
        }


class MessageUpdate(BaseModel):
    """Schema để edit message"""
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Schema response cho message"""
    message_id: int
    channel_id: int
    sender_id: UUID
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    content: Optional[str]
    sent_at: datetime
    is_edited: bool = False
    reply_to_id: Optional[int] = None

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema response cho danh sách messages (có pagination)"""
    messages: List[MessageResponse]
    total: int
    has_more: bool
    skip: int
    limit: int


# ==========================================
# MEETING SCHEMAS
# ==========================================

class MeetingCreate(BaseModel):
    """Schema để tạo meeting mới"""
    team_id: int = Field(..., description="ID của team")
    title: str = Field(..., min_length=1, max_length=200, description="Tiêu đề cuộc họp")
    start_time: datetime = Field(..., description="Thời gian bắt đầu")
    end_time: Optional[datetime] = Field(None, description="Thời gian kết thúc")
    link_url: Optional[str] = Field(None, description="Link cuộc họp (PeerJS room ID hoặc external link)")

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": 1,
                "title": "Sprint Planning",
                "start_time": "2026-02-10T09:00:00Z",
                "end_time": "2026-02-10T10:00:00Z",
                "link_url": None
            }
        }


class MeetingUpdate(BaseModel):
    """Schema để cập nhật meeting"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    link_url: Optional[str] = None


class MeetingResponse(BaseModel):
    """Schema response cho meeting"""
    meeting_id: int
    team_id: int
    title: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    link_url: Optional[str]
    organizer_id: UUID
    organizer_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingJoinResponse(BaseModel):
    """Schema response khi join meeting"""
    meeting_id: int
    room_id: str  # PeerJS room ID
    participants: List[dict] = []  # [{user_id, name, peer_id}]
