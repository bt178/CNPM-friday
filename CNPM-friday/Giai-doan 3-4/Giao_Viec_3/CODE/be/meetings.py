"""
Meetings API Endpoints - Phase 3
Copy file này vào: backend/app/api/v1/meetings.py
Sau đó register router trong api.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.all_models import Meeting, TeamMember, User, Team

from pydantic import BaseModel, Field

# ========== SCHEMAS (inline, sau đó move ra schemas/meeting.py) ==========

class MeetingCreate(BaseModel):
    team_id: int
    title: str = Field(..., min_length=1, max_length=200)
    start_time: datetime
    end_time: Optional[datetime] = None
    link_url: Optional[str] = None

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    link_url: Optional[str] = None

class MeetingResponse(BaseModel):
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
    meeting_id: int
    room_id: str
    meeting_url: str
    participants: List[dict] = []

# ========== ROUTER ==========

router = APIRouter()


@router.post("/", response_model=MeetingResponse, status_code=201)
async def schedule_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo cuộc họp mới cho team.
    Chỉ team members mới có quyền tạo.
    """
    # Kiểm tra team tồn tại
    team = await db.get(Team, meeting_data.team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team không tồn tại"
        )
    
    # Kiểm tra user có phải team member không
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == meeting_data.team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    if not member_check.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn phải là thành viên của team mới có thể tạo cuộc họp"
        )
    
    # Tạo room ID cho PeerJS nếu không có link
    room_id = meeting_data.link_url or f"meeting-{uuid4().hex[:8]}"
    
    # Tạo meeting
    new_meeting = Meeting(
        team_id=meeting_data.team_id,
        title=meeting_data.title,
        start_time=meeting_data.start_time,
        end_time=meeting_data.end_time,
        link_url=room_id,
        organizer_id=current_user.user_id
    )
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)
    
    return MeetingResponse(
        meeting_id=new_meeting.meeting_id,
        team_id=new_meeting.team_id,
        title=new_meeting.title,
        start_time=new_meeting.start_time,
        end_time=new_meeting.end_time,
        link_url=new_meeting.link_url,
        organizer_id=new_meeting.organizer_id,
        organizer_name=current_user.full_name,
        created_at=new_meeting.created_at
    )


@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    team_id: int,
    upcoming_only: bool = Query(False, description="Chỉ lấy meetings sắp diễn ra"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách meetings của team.
    """
    # Kiểm tra user có phải team member không
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    if not member_check.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem meetings của team này"
        )
    
    # Build query
    query = select(Meeting).where(Meeting.team_id == team_id)
    
    if upcoming_only:
        query = query.where(Meeting.start_time >= datetime.utcnow())
    
    query = query.order_by(Meeting.start_time)
    
    result = await db.execute(query)
    meetings = result.scalars().all()
    
    response = []
    for meeting in meetings:
        # Lấy organizer name
        organizer = await db.get(User, meeting.organizer_id)
        organizer_name = organizer.full_name if organizer else "Unknown"
        
        response.append(MeetingResponse(
            meeting_id=meeting.meeting_id,
            team_id=meeting.team_id,
            title=meeting.title,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            link_url=meeting.link_url,
            organizer_id=meeting.organizer_id,
            organizer_name=organizer_name,
            created_at=meeting.created_at
        ))
    
    return response


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lấy chi tiết meeting."""
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting không tồn tại"
        )
    
    organizer = await db.get(User, meeting.organizer_id)
    
    return MeetingResponse(
        meeting_id=meeting.meeting_id,
        team_id=meeting.team_id,
        title=meeting.title,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        link_url=meeting.link_url,
        organizer_id=meeting.organizer_id,
        organizer_name=organizer.full_name if organizer else "Unknown",
        created_at=meeting.created_at
    )


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    update_data: MeetingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cập nhật meeting.
    Chỉ organizer mới có quyền cập nhật.
    """
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting không tồn tại"
        )
    
    # Kiểm tra có phải organizer không
    if meeting.organizer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ người tạo meeting mới có quyền cập nhật"
        )
    
    # Cập nhật
    if update_data.title is not None:
        meeting.title = update_data.title
    if update_data.start_time is not None:
        meeting.start_time = update_data.start_time
    if update_data.end_time is not None:
        meeting.end_time = update_data.end_time
    if update_data.link_url is not None:
        meeting.link_url = update_data.link_url
    
    await db.commit()
    await db.refresh(meeting)
    
    return MeetingResponse(
        meeting_id=meeting.meeting_id,
        team_id=meeting.team_id,
        title=meeting.title,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        link_url=meeting.link_url,
        organizer_id=meeting.organizer_id,
        organizer_name=current_user.full_name,
        created_at=meeting.created_at
    )


@router.delete("/{meeting_id}", status_code=204)
async def cancel_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Hủy meeting.
    Chỉ organizer mới có quyền hủy.
    """
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting không tồn tại"
        )
    
    if meeting.organizer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ người tạo meeting mới có quyền hủy"
        )
    
    await db.delete(meeting)
    await db.commit()
    return None


@router.post("/{meeting_id}/join", response_model=MeetingJoinResponse)
async def join_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Tham gia meeting.
    Trả về room ID để connect PeerJS.
    """
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting không tồn tại"
        )
    
    # Kiểm tra user có phải team member không
    member_check = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == meeting.team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    if not member_check.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền tham gia meeting này"
        )
    
    # Tạo peer_id cho user
    peer_id = f"peer-{current_user.user_id.hex[:8]}"
    
    return MeetingJoinResponse(
        meeting_id=meeting.meeting_id,
        room_id=meeting.link_url or f"meeting-{meeting_id}",
        meeting_url=f"/meetings/{meeting_id}",
        participants=[{
            "user_id": str(current_user.user_id),
            "name": current_user.full_name,
            "peer_id": peer_id
        }]
    )
