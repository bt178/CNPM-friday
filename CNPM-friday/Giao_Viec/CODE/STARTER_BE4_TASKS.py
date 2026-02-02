"""
BE4 - Tasks & Sprint Endpoints
Starter template
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional

from app.api import deps
from app.models.all_models import Task, Sprint, User

router = APIRouter()

# ===== SCHEMAS (Add to app/schemas/task.py) =====
# from pydantic import BaseModel
# from typing import Optional
# 
# class TaskCreate(BaseModel):
#     title: str
#     description: Optional[str] = None
#     sprint_id: int
#     assigned_to: Optional[str] = None  # user_id
#     priority: str = "MEDIUM"
#
# class TaskUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     status: Optional[str] = None
#     assigned_to: Optional[str] = None
#     priority: Optional[str] = None


@router.post("/tasks", tags=["tasks"])
async def create_task(
    title: str,
    sprint_id: int,
    description: str = "",
    assigned_to: Optional[str] = None,
    priority: str = "MEDIUM",
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new task in a sprint"""
    
    # Verify sprint exists
    sprint = await db.get(Sprint, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    task = Task(
        title=title,
        description=description,
        sprint_id=sprint_id,
        assigned_to=assigned_to,
        status="TODO",
        priority=priority,
        created_by=current_user.user_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return {
        "task_id": task.task_id,
        "title": task.title,
        "sprint_id": sprint_id,
        "status": "TODO",
        "priority": priority,
        "created_by": str(current_user.user_id),
        "created_at": task.created_at.isoformat()
    }


@router.get("/tasks", tags=["tasks"])
async def list_tasks(
    sprint_id: Optional[int] = None,
    team_id: Optional[int] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List tasks
    Filter by sprint_id or team_id
    """
    query = select(Task)
    
    if sprint_id:
        query = query.where(Task.sprint_id == sprint_id)
    
    result = await db.execute(query.order_by(Task.created_at.desc()))
    tasks = result.scalars().all()
    
    return [
        {
            "task_id": t.task_id,
            "title": t.title,
            "description": t.description,
            "sprint_id": t.sprint_id,
            "status": t.status,
            "priority": t.priority,
            "assigned_to": str(t.assigned_to) if t.assigned_to else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tasks
    ]


@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task_detail(
    task_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get task details"""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "title": task.title,
        "description": task.description,
        "sprint_id": task.sprint_id,
        "status": task.status,
        "priority": task.priority,
        "assigned_to": str(task.assigned_to) if task.assigned_to else None,
        "created_by": str(task.created_by),
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


@router.put("/tasks/{task_id}", tags=["tasks"])
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update task (status, assigned_to, etc.)"""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate status
    if status:
        valid_statuses = ["TODO", "DOING", "DONE", "BLOCKED"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
        task.status = status
    
    if title:
        task.title = title
    if description is not None:
        task.description = description
    if assigned_to:
        task.assigned_to = assigned_to
    if priority:
        task.priority = priority
    
    task.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(task)
    
    return {
        "task_id": task.task_id,
        "title": task.title,
        "status": task.status,
        "assigned_to": str(task.assigned_to) if task.assigned_to else None,
        "updated_at": task.updated_at.isoformat()
    }


@router.delete("/tasks/{task_id}", tags=["tasks"])
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a task"""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Task deleted successfully", "task_id": task_id}


# ===== SPRINT ENDPOINTS =====

@router.post("/sprints", tags=["sprints"])
async def create_sprint(
    name: str,
    team_id: int,
    duration_days: int = 7,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new sprint for a team"""
    sprint = Sprint(
        name=name,
        team_id=team_id,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc),  # Can be calculated from duration
        status="ACTIVE",
        created_by=current_user.user_id,
    )
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    
    return {
        "sprint_id": sprint.sprint_id,
        "name": sprint.name,
        "team_id": team_id,
        "status": "ACTIVE"
    }


@router.get("/sprints/{sprint_id}", tags=["sprints"])
async def get_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get sprint details with tasks"""
    sprint = await db.get(Sprint, sprint_id)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Get tasks in sprint
    result = await db.execute(select(Task).where(Task.sprint_id == sprint_id))
    tasks = result.scalars().all()
    
    # Count by status
    todo_count = sum(1 for t in tasks if t.status == "TODO")
    doing_count = sum(1 for t in tasks if t.status == "DOING")
    done_count = sum(1 for t in tasks if t.status == "DONE")
    
    return {
        "sprint_id": sprint.sprint_id,
        "name": sprint.name,
        "team_id": sprint.team_id,
        "status": sprint.status,
        "task_count": len(tasks),
        "tasks_by_status": {
            "TODO": todo_count,
            "DOING": doing_count,
            "DONE": done_count
        }
    }
