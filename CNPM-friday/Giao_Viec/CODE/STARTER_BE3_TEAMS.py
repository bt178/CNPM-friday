"""
BE3 - Teams & Join Code Endpoints
Starter template
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.api import deps
from app.models.all_models import Team, TeamMember, User

router = APIRouter()

# ===== SCHEMAS (Add to app/schemas/team.py) =====
# from pydantic import BaseModel
# 
# class TeamCreate(BaseModel):
#     name: str
#     project_id: int
#     description: str = ""


@router.post("/teams", tags=["teams"])
async def create_team(
    name: str,
    project_id: int,
    description: str = "",
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Student creates a new team
    Auto-generate join_code and add creator as LEADER
    """
    if current_user.role_id != 5:  # Only students
        raise HTTPException(status_code=403, detail="Only students can create teams")
    
    # Create team with auto-generated join code
    team = Team(
        name=name,
        project_id=project_id,
        description=description,
        join_code=secrets.token_hex(3).upper(),  # e.g., "A1B2C3"
        created_by=current_user.user_id,
        is_finalized=False,
        created_at=datetime.now(timezone.utc)
    )
    db.add(team)
    await db.flush()  # Get team_id without commit
    
    # Auto-add creator as LEADER
    team_member = TeamMember(
        team_id=team.team_id,
        user_id=current_user.user_id,
        role="LEADER",
        joined_at=datetime.now(timezone.utc)
    )
    db.add(team_member)
    await db.commit()
    await db.refresh(team)
    
    return {
        "team_id": team.team_id,
        "name": team.name,
        "join_code": team.join_code,
        "project_id": project_id,
        "created_by": str(current_user.user_id),
        "member_count": 1
    }


@router.get("/teams", tags=["teams"])
async def list_teams(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """List all teams"""
    result = await db.execute(select(Team).order_by(Team.created_at.desc()))
    teams = result.scalars().all()
    
    return [
        {
            "team_id": t.team_id,
            "name": t.name,
            "project_id": t.project_id,
            "join_code": t.join_code if not t.is_finalized else "***",
            "is_finalized": t.is_finalized,
            "created_by": str(t.created_by),
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in teams
    ]


@router.get("/teams/{team_id}", tags=["teams"])
async def get_team_detail(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get team details with members list"""
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get team members
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    members = result.scalars().all()
    
    return {
        "team_id": team.team_id,
        "name": team.name,
        "project_id": team.project_id,
        "description": team.description,
        "join_code": team.join_code if not team.is_finalized else None,
        "is_finalized": team.is_finalized,
        "created_by": str(team.created_by),
        "created_at": team.created_at.isoformat() if team.created_at else None,
        "member_count": len(members),
        "members": [
            {
                "user_id": str(m.user_id),
                "role": m.role,
                "joined_at": m.joined_at.isoformat() if m.joined_at else None
            }
            for m in members
        ]
    }


@router.post("/teams/join", tags=["teams"])
async def join_team(
    join_code: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Student joins a team using join_code
    Cannot join if team is finalized
    """
    if current_user.role_id != 5:  # Only students
        raise HTTPException(status_code=403, detail="Only students can join teams")
    
    # Find team by join_code
    result = await db.execute(select(Team).where(Team.join_code == join_code))
    team = result.scalars().first()
    
    if not team:
        raise HTTPException(status_code=404, detail="Team not found with this code")
    
    if team.is_finalized:
        raise HTTPException(status_code=400, detail="Team is finalized, cannot join")
    
    # Check if already a member
    existing = await db.execute(
        select(TeamMember).where(
            (TeamMember.team_id == team.team_id) & 
            (TeamMember.user_id == current_user.user_id)
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Already a member of this team")
    
    # Add as member
    team_member = TeamMember(
        team_id=team.team_id,
        user_id=current_user.user_id,
        role="MEMBER",
        joined_at=datetime.now(timezone.utc)
    )
    db.add(team_member)
    await db.commit()
    
    return {
        "team_id": team.team_id,
        "name": team.name,
        "message": f"Successfully joined {team.name}"
    }


@router.post("/teams/{team_id}/leave", tags=["teams"])
async def leave_team(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Student leaves a team (cannot be LEADER)"""
    if current_user.role_id != 5:
        raise HTTPException(status_code=403, detail="Only students can leave teams")
    
    # Find member record
    result = await db.execute(
        select(TeamMember).where(
            (TeamMember.team_id == team_id) & 
            (TeamMember.user_id == current_user.user_id)
        )
    )
    member = result.scalars().first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Not a member of this team")
    
    if member.role == "LEADER":
        raise HTTPException(status_code=400, detail="Leader cannot leave team")
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "Left team successfully"}


@router.patch("/teams/{team_id}/finalize", tags=["teams"])
async def finalize_team(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Finalize team (lock from join/leave)
    Only LECTURER (4) or ADMIN (1) can finalize
    """
    if current_user.role_id not in [1, 4]:
        raise HTTPException(status_code=403, detail="Only lecturers can finalize teams")
    
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team.is_finalized:
        raise HTTPException(status_code=400, detail="Team already finalized")
    
    team.is_finalized = True
    team.finalized_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(team)
    
    return {
        "team_id": team.team_id,
        "is_finalized": True,
        "message": "Team finalized successfully"
    }
