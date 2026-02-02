"""
BE4 - Tasks & Sprints Endpoints
Author: Backend Dev 4
Created: 2026-01-28

Description:
- Create/manage tasks in sprints
- Status transitions: TODO → DOING → DONE
- Assign tasks to team members
- Simple priority levels (LOW, MEDIUM, HIGH)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Optional

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.all_models import User, Sprint, Task
from app.schemas.task import TaskCreate, TaskUpdate

router = APIRouter()

# ============================================================================
# SPRINTS ENDPOINTS
# ============================================================================

@router.post("/sprints", status_code=201)
async def create_sprint(
    team_id: int,
    name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a sprint for a team
    
    Request Query/Body:
        {
            "team_id": 1,
            "name": "Sprint 1 - Setup",
            "start_date": "2026-01-28",
            "end_date": "2026-02-04"
        }
    
    Response:
        {
            "sprint_id": 1,
            "team_id": 1,
            "name": "Sprint 1",
            "start_date": "2026-01-28",
            "end_date": "2026-02-04",
            "created_at": "2026-01-28T10:00:00"
        }
    """
    
    sprint = Sprint(
        team_id=team_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        created_by=current_user.user_id,
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    
    return {
        "sprint_id": sprint.sprint_id,
        "team_id": sprint.team_id,
        "name": sprint.name,
        "start_date": sprint.start_date,
        "end_date": sprint.end_date,
        "created_at": sprint.created_at
    }


@router.get("/sprints/{sprint_id}")
async def get_sprint_detail(
    sprint_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sprint details with task counts by status
    
    Response:
        {
            "sprint_id": 1,
            "team_id": 1,
            "name": "Sprint 1",
            "start_date": "2026-01-28",
            "end_date": "2026-02-04",
            "task_counts": {
                "TODO": 5,
                "DOING": 2,
                "DONE": 3,
                "BLOCKED": 1
            },
            "created_at": "2026-01-28T10:00:00"
        }
    """
    
    query = select(Sprint).where(Sprint.sprint_id == sprint_id)
    result = await db.execute(query)
    sprint = result.scalar()
    
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint not found"
        )
    
    # Count tasks by status
    tasks_query = select(Task).where(Task.sprint_id == sprint_id)
    tasks_result = await db.execute(tasks_query)
    all_tasks = tasks_result.scalars().all()
    
    task_counts = {
        "TODO": sum(1 for t in all_tasks if t.status == "TODO"),
        "DOING": sum(1 for t in all_tasks if t.status == "DOING"),
        "DONE": sum(1 for t in all_tasks if t.status == "DONE"),
        "BLOCKED": sum(1 for t in all_tasks if t.status == "BLOCKED"),
    }
    
    return {
        "sprint_id": sprint.sprint_id,
        "team_id": sprint.team_id,
        "name": sprint.name,
        "start_date": sprint.start_date,
        "end_date": sprint.end_date,
        "task_counts": task_counts,
        "total_tasks": len(all_tasks),
        "created_at": sprint.created_at
    }


# ============================================================================
# TASKS ENDPOINTS
# ============================================================================

@router.post("", status_code=201)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task in a sprint
    
    Request:
        {
            "title": "Setup project structure",
            "sprint_id": 1,
            "description": "Create folders and initial files",
            "assigned_to": "student-uuid-1",
            "priority": "HIGH"
        }
    
    Response:
        {
            "task_id": 1,
            "title": "Setup project structure",
            "sprint_id": 1,
            "status": "TODO",
            "priority": "HIGH",
            "assigned_to": "student-uuid-1",
            "created_by": "student@example.com",
            "created_at": "2026-01-28T10:00:00"
        }
    """
    
    new_task = Task(
        title=task.title,
        sprint_id=task.sprint_id,
        description=task.description,
        status="TODO",
        priority=task.priority or "MEDIUM",
        assigned_to=task.assigned_to,
        created_by=current_user.user_id,
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # Get assigned user name if applicable
    assigned_name = None
    if new_task.assigned_to:
        user_query = select(User).where(User.user_id == new_task.assigned_to)
        user_result = await db.execute(user_query)
        assigned_user = user_result.scalar()
        assigned_name = assigned_user.full_name if assigned_user else None
    
    return {
        "task_id": new_task.task_id,
        "title": new_task.title,
        "sprint_id": new_task.sprint_id,
        "description": new_task.description,
        "status": new_task.status,
        "priority": new_task.priority,
        "assigned_to": assigned_name,
        "created_by": current_user.full_name,
        "created_at": new_task.created_at
    }


@router.get("")
async def get_tasks(
    sprint_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tasks (optionally filter by sprint_id or status)
    
    Query params:
        ?sprint_id=1&status=TODO
    
    Response:
        {
            "tasks": [
                {
                    "task_id": 1,
                    "title": "Setup project",
                    "sprint_id": 1,
                    "status": "TODO",
                    "priority": "HIGH",
                    "assigned_to": "John Doe",
                    "created_by": "Jane Smith"
                },
                ...
            ],
            "total": 5
        }
    """
    
    query = select(Task)
    
    # Filter by sprint
    if sprint_id:
        query = query.where(Task.sprint_id == sprint_id)
    
    # Filter by status
    if status:
        valid_statuses = ["TODO", "DOING", "DONE", "BLOCKED"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {valid_statuses}"
            )
        query = query.where(Task.status == status)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    tasks_response = []
    for t in tasks:
        # Get assigned user name
        assigned_name = None
        if t.assigned_to:
            user_query = select(User).where(User.user_id == t.assigned_to)
            user_result = await db.execute(user_query)
            assigned_user = user_result.scalar()
            assigned_name = assigned_user.full_name if assigned_user else None
        
        # Get creator name
        creator_query = select(User).where(User.user_id == t.created_by)
        creator_result = await db.execute(creator_query)
        creator = creator_result.scalar()
        
        tasks_response.append({
            "task_id": t.task_id,
            "title": t.title,
            "sprint_id": t.sprint_id,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assigned_to": assigned_name,
            "created_by": creator.full_name if creator else "Unknown",
            "created_at": t.created_at
        })
    
    return {
        "tasks": tasks_response,
        "total": len(tasks_response)
    }


@router.get("/{task_id}")
async def get_task_detail(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get task details
    
    Response:
        {
            "task_id": 1,
            "title": "Setup project",
            "sprint_id": 1,
            "description": "...",
            "status": "TODO",
            "priority": "HIGH",
            "assigned_to": "John Doe",
            "created_by": "Jane Smith",
            "created_at": "2026-01-28T10:00:00",
            "updated_at": "2026-01-28T10:00:00"
        }
    """
    
    query = select(Task).where(Task.task_id == task_id)
    result = await db.execute(query)
    task = result.scalar()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get assigned user name
    assigned_name = None
    if task.assigned_to:
        user_query = select(User).where(User.user_id == task.assigned_to)
        user_result = await db.execute(user_query)
        assigned_user = user_result.scalar()
        assigned_name = assigned_user.full_name if assigned_user else None
    
    # Get creator name
    creator_query = select(User).where(User.user_id == task.created_by)
    creator_result = await db.execute(creator_query)
    creator = creator_result.scalar()
    
    return {
        "task_id": task.task_id,
        "title": task.title,
        "sprint_id": task.sprint_id,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assigned_to": assigned_name,
        "created_by": creator.full_name if creator else "Unknown",
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }


@router.put("/{task_id}", status_code=200)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update task details (title, description, status, priority, assigned_to)
    - Status must be one of: TODO, DOING, DONE, BLOCKED
    
    Request:
        {
            "title": "Setup project structure",
            "status": "DOING",
            "priority": "HIGH",
            "assigned_to": "student-uuid-1"
        }
    
    Response:
        {
            "task_id": 1,
            "title": "Setup project structure",
            "status": "DOING",
            "priority": "HIGH",
            "assigned_to": "John Doe",
            "updated_at": "2026-01-28T10:30:00"
        }
    """
    
    # Get task
    query = select(Task).where(Task.task_id == task_id)
    result = await db.execute(query)
    task = result.scalar()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update fields if provided
    if task_update.title is not None:
        task.title = task_update.title
    
    if task_update.description is not None:
        task.description = task_update.description
    
    # Validate status
    if task_update.status is not None:
        valid_statuses = ["TODO", "DOING", "DONE", "BLOCKED"]
        if task_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be one of: {valid_statuses}"
            )
        task.status = task_update.status
    
    if task_update.priority is not None:
        task.priority = task_update.priority
    
    if task_update.assigned_to is not None:
        task.assigned_to = task_update.assigned_to
    
    # Update timestamp
    task.updated_at = datetime.now(timezone.utc)
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Get assigned user name
    assigned_name = None
    if task.assigned_to:
        user_query = select(User).where(User.user_id == task.assigned_to)
        user_result = await db.execute(user_query)
        assigned_user = user_result.scalar()
        assigned_name = assigned_user.full_name if assigned_user else None
    
    return {
        "task_id": task.task_id,
        "title": task.title,
        "sprint_id": task.sprint_id,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assigned_to": assigned_name,
        "updated_at": task.updated_at
    }


@router.delete("/{task_id}", status_code=200)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task
    
    Response:
        {
            "task_id": 1,
            "message": "Task deleted successfully"
        }
    """
    
    # Get task
    query = select(Task).where(Task.task_id == task_id)
    result = await db.execute(query)
    task = result.scalar()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Delete
    await db.delete(task)
    await db.commit()
    
    return {
        "task_id": task_id,
        "message": "Task deleted successfully"
    }
