"""
BE3 - Teams & Join Logic Endpoints
Author: Backend Dev 3
Created: 2026-01-28

Description:
- Students create teams (auto-generates join_code)
- Creator becomes LEADER
- Other students join via join_code
- Lecturer finalizes team (locks join_code)
- Auto-add creator as LEADER team member
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional
import secrets

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.all_models import User, Team, TeamMember
from app.schemas.team import TeamCreate, TeamResponse

router = APIRouter()

# ============================================================================
# TEAMS ENDPOINTS
# ============================================================================

@router.post("", status_code=201)
async def create_team(
    team: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new team (Student only)
    - Auto-generates join_code (6 hex chars = 3 bytes)
    - Creator becomes LEADER
    - Team not finalized (can still join)
    
    Request:
        {
            "name": "Team A",
            "project_id": 1,
            "description": "Web development team"
        }
    
    Response:
        {
            "team_id": 1,
            "name": "Team A",
            "project_id": 1,
            "join_code": "A1B2C3",
            "is_finalized": false,
            "created_by": "student@example.com",
            "member_count": 1
        }
    """
    
    # Role check: only students (role_id=5) can create teams
    if current_user.role_id != 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create teams"
        )
    
    # Generate unique join_code (6 hex chars = cryptographically random)
    join_code = secrets.token_hex(3).upper()
    
    # Create new team
    new_team = Team(
        name=team.name,
        project_id=team.project_id,
        description=team.description,
        join_code=join_code,
        is_finalized=False,
        created_by=current_user.user_id,
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(new_team)
    await db.flush()  # ← Important! Need team_id before creating member
    
    # Auto-add creator as LEADER
    team_member = TeamMember(
        team_id=new_team.team_id,
        user_id=current_user.user_id,
        role="LEADER",
        joined_at=datetime.now(timezone.utc),
    )
    
    db.add(team_member)
    await db.commit()
    await db.refresh(new_team)
    
    return {
        "team_id": new_team.team_id,
        "name": new_team.name,
        "project_id": new_team.project_id,
        "description": new_team.description,
        "join_code": new_team.join_code,
        "is_finalized": new_team.is_finalized,
        "created_by": current_user.full_name,
        "member_count": 1
    }


@router.get("")
async def get_teams(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all teams (optionally filter by project_id)
    
    Query params:
        ?project_id=1  (filters by project)
    
    Response:
        {
            "teams": [
                {
                    "team_id": 1,
                    "name": "Team A",
                    "project_id": 1,
                    "member_count": 3,
                    "is_finalized": false,
                    "created_by": "student@example.com"
                },
                ...
            ],
            "total": 5
        }
    """
    
    query = select(Team)
    
    if project_id:
        query = query.where(Team.project_id == project_id)
    
    result = await db.execute(query)
    teams = result.scalars().all()
    
    teams_response = []
    for t in teams:
        # Count members
        member_query = select(TeamMember).where(TeamMember.team_id == t.team_id)
        member_result = await db.execute(member_query)
        members = member_result.scalars().all()
        
        # Get creator name
        creator_query = select(User).where(User.user_id == t.created_by)
        creator_result = await db.execute(creator_query)
        creator = creator_result.scalar()
        
        teams_response.append({
            "team_id": t.team_id,
            "name": t.name,
            "project_id": t.project_id,
            "description": t.description,
            "member_count": len(members),
            "is_finalized": t.is_finalized,
            "created_by": creator.full_name if creator else "Unknown",
            "created_at": t.created_at
        })
    
    return {
        "teams": teams_response,
        "total": len(teams_response)
    }


@router.get("/{team_id}")
async def get_team_detail(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get team details including members list
    
    Response:
        {
            "team_id": 1,
            "name": "Team A",
            "project_id": 1,
            "description": "...",
            "join_code": "A1B2C3",
            "is_finalized": false,
            "created_by": "student@example.com",
            "created_at": "2026-01-28T10:00:00",
            "members": [
                {
                    "user_id": "uuid-1",
                    "full_name": "John Doe",
                    "role": "LEADER",
                    "joined_at": "2026-01-28T10:00:00"
                },
                {
                    "user_id": "uuid-2",
                    "full_name": "Jane Smith",
                    "role": "MEMBER",
                    "joined_at": "2026-01-28T10:30:00"
                }
            ]
        }
    """
    
    # Get team
    query = select(Team).where(Team.team_id == team_id)
    result = await db.execute(query)
    team = result.scalar()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get creator info
    creator_query = select(User).where(User.user_id == team.created_by)
    creator_result = await db.execute(creator_query)
    creator = creator_result.scalar()
    
    # Get members
    member_query = select(TeamMember).where(TeamMember.team_id == team_id)
    member_result = await db.execute(member_query)
    team_members = member_result.scalars().all()
    
    members_response = []
    for tm in team_members:
        # Get user info
        user_query = select(User).where(User.user_id == tm.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar()
        
        members_response.append({
            "user_id": tm.user_id,
            "full_name": user.full_name if user else "Unknown",
            "role": tm.role,
            "joined_at": tm.joined_at
        })
    
    return {
        "team_id": team.team_id,
        "name": team.name,
        "project_id": team.project_id,
        "description": team.description,
        "join_code": team.join_code if not team.is_finalized else None,
        "is_finalized": team.is_finalized,
        "created_by": creator.full_name if creator else "Unknown",
        "created_at": team.created_at,
        "members": members_response,
        "member_count": len(members_response)
    }


@router.post("/{team_id}/join", status_code=200)
async def join_team(
    team_id: int,
    join_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Join a team using join_code
    - Validates join_code matches
    - Validates team not finalized
    - Adds user as MEMBER
    
    Request:
        {
            "join_code": "A1B2C3"
        }
    
    Response:
        {
            "team_id": 1,
            "message": "Successfully joined team",
            "role": "MEMBER",
            "joined_at": "2026-01-28T10:30:00"
        }
    """
    
    # Get team
    query = select(Team).where(Team.team_id == team_id)
    result = await db.execute(query)
    team = result.scalar()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check if team is finalized
    if team.is_finalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is finalized and cannot accept new members"
        )
    
    # Validate join_code
    if team.join_code != join_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid join code"
        )
    
    # Check if already member
    member_query = select(TeamMember).where(
        and_(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    member_result = await db.execute(member_query)
    existing_member = member_result.scalar()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this team"
        )
    
    # Add user to team
    new_member = TeamMember(
        team_id=team_id,
        user_id=current_user.user_id,
        role="MEMBER",
        joined_at=datetime.now(timezone.utc),
    )
    
    db.add(new_member)
    await db.commit()
    
    return {
        "team_id": team_id,
        "message": "Successfully joined team",
        "role": "MEMBER",
        "joined_at": new_member.joined_at
    }


@router.post("/{team_id}/leave", status_code=200)
async def leave_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Leave a team (remove yourself as member)
    
    Response:
        {
            "team_id": 1,
            "message": "Successfully left team"
        }
    """
    
    # Get team
    query = select(Team).where(Team.team_id == team_id)
    result = await db.execute(query)
    team = result.scalar()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get member record
    member_query = select(TeamMember).where(
        and_(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.user_id
        )
    )
    member_result = await db.execute(member_query)
    member = member_result.scalar()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this team"
        )
    
    # Delete member record
    await db.delete(member)
    await db.commit()
    
    return {
        "team_id": team_id,
        "message": "Successfully left team"
    }


@router.patch("/{team_id}/finalize", status_code=200)
async def finalize_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Finalize team (lock it - no more members can join)
    - Only Lecturer/Admin can finalize
    - Removes join_code
    
    Response:
        {
            "team_id": 1,
            "message": "Team finalized",
            "is_finalized": true
        }
    """
    
    # Role check: only lecturers (4) and admins (1) can finalize
    if current_user.role_id not in [1, 4]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers or admins can finalize teams"
        )
    
    # Get team
    query = select(Team).where(Team.team_id == team_id)
    result = await db.execute(query)
    team = result.scalar()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Already finalized?
    if team.is_finalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is already finalized"
        )
    
    # Finalize
    team.is_finalized = True
    team.join_code = None  # Clear join code
    
    db.add(team)
    await db.commit()
    
    return {
        "team_id": team_id,
        "message": "Team finalized",
        "is_finalized": True
    }
