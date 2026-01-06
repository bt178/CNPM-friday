"""
FastAPI endpoints for Task Board (Kanban-style) management.
Ticket: BE-TASK-01
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.all_models import Sprint, Task, Team, TeamMember, User
from app.schemas.task import (
    SprintCreate,
    SprintResponse,
    SprintUpdate,
    TaskBoardResponse,
    TaskCreate,
    TaskResponse,
    TaskStatistics,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def verify_team_member(
    db: AsyncSession,
    team_id: int,
    user_id: UUID,
) -> bool:
    """Check if user is a member of the team."""
    result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.student_id == user_id,
                TeamMember.is_active == True,
            )
        )
    )
    return result.scalar_one_or_none() is not None


# ==========================================
# SPRINT ENDPOINTS
# ==========================================

@router.post("/sprints", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    sprint_in: SprintCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new Sprint for a team.
    Only team members can create sprints.
    """
    if current_user.role.role_name.upper() != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create sprints",
        )

    # Verify team exists
    team_result = await db.execute(
        select(Team).where(Team.team_id == sprint_in.team_id)
    )
    if not team_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {sprint_in.team_id} not found",
        )

    # Verify user is team member
    if not await verify_team_member(db, sprint_in.team_id, current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    # Create sprint
    new_sprint = Sprint(
        team_id=sprint_in.team_id,
        title=sprint_in.title,
        start_date=sprint_in.start_date,
        end_date=sprint_in.end_date,
        status="planned",
    )

    db.add(new_sprint)
    await db.commit()
    await db.refresh(new_sprint)

    response = SprintResponse.model_validate(new_sprint)
    response.task_count = 0
    return response


@router.get("/teams/{team_id}/sprints", response_model=list[SprintResponse])
async def list_sprints(
    team_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List all sprints for a team."""
    # Verify team exists
    team_result = await db.execute(
        select(Team).where(Team.team_id == team_id)
    )
    if not team_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )

    # Verify access (team member or lecturer)
    user_role = current_user.role.role_name.upper()
    if user_role == "STUDENT":
        if not await verify_team_member(db, team_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

    # Get sprints with task count
    result = await db.execute(
        select(Sprint)
        .options(selectinload(Sprint.tasks))
        .where(Sprint.team_id == team_id)
        .order_by(Sprint.start_date.desc())
    )
    sprints = result.scalars().all()

    responses = []
    for sprint in sprints:
        resp = SprintResponse.model_validate(sprint)
        resp.task_count = len(sprint.tasks) if sprint.tasks else 0
        responses.append(resp)

    return responses


@router.get("/sprints/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get Sprint details."""
    result = await db.execute(
        select(Sprint)
        .options(selectinload(Sprint.tasks))
        .where(Sprint.sprint_id == sprint_id)
    )
    sprint = result.scalar_one_or_none()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found",
        )

    # Verify access
    user_role = current_user.role.role_name.upper()
    if user_role == "STUDENT":
        if not await verify_team_member(db, sprint.team_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

    response = SprintResponse.model_validate(sprint)
    response.task_count = len(sprint.tasks) if sprint.tasks else 0
    return response


@router.patch("/sprints/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: int,
    sprint_in: SprintUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update Sprint details. Only team members can update."""
    result = await db.execute(
        select(Sprint).where(Sprint.sprint_id == sprint_id)
    )
    sprint = result.scalar_one_or_none()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found",
        )

    # Verify team membership
    if current_user.role.role_name.upper() == "STUDENT":
        if not await verify_team_member(db, sprint.team_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

    # Validate status
    if sprint_in.status and sprint_in.status not in ["planned", "active", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be: planned, active, completed",
        )

    # Update fields
    update_data = sprint_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sprint, field, value)

    await db.commit()
    await db.refresh(sprint)

    # Get task count
    task_count_result = await db.execute(
        select(func.count()).select_from(Task).where(Task.sprint_id == sprint_id)
    )
    task_count = task_count_result.scalar()

    response = SprintResponse.model_validate(sprint)
    response.task_count = task_count
    return response


@router.delete("/sprints/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    sprint_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete Sprint.
    Only team leader can delete sprints.
    """
    result = await db.execute(
        select(Sprint)
        .join(Team)
        .where(Sprint.sprint_id == sprint_id)
    )
    sprint = result.scalar_one_or_none()

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found",
        )

    # Get team to check leadership
    team_result = await db.execute(
        select(Team).where(Team.team_id == sprint.team_id)
    )
    team = team_result.scalar_one_or_none()

    if current_user.role.role_name.upper() == "STUDENT":
        if team.leader_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leader can delete sprints",
            )

    await db.delete(sprint)
    await db.commit()
    return None


# ==========================================
# TASK ENDPOINTS
# ==========================================

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a new Task.
    Only team members can create tasks.
    If sprint_id is null, task goes to backlog.
    """
    if current_user.role.role_name.upper() != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create tasks",
        )

    # Get sprint to verify team membership
    team_id = None
    if task_in.sprint_id:
        sprint_result = await db.execute(
            select(Sprint).where(Sprint.sprint_id == task_in.sprint_id)
        )
        sprint = sprint_result.scalar_one_or_none()
        if not sprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sprint {task_in.sprint_id} not found",
            )
        team_id = sprint.team_id
    else:
        # For backlog tasks, we need team_id from request (you might want to add this to TaskCreate)
        # For now, we'll require sprint_id
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sprint_id is required. Use team sprints or create a sprint first",
        )

    # Verify team membership
    if not await verify_team_member(db, team_id, current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    # Verify assignee is team member if provided
    if task_in.assignee_id:
        if not await verify_team_member(db, team_id, task_in.assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a member of this team",
            )

    # Create task
    new_task = Task(
        sprint_id=task_in.sprint_id,
        title=task_in.title,
        description=task_in.description,
        assignee_id=task_in.assignee_id,
        priority=task_in.priority or "medium",
        status="todo",
        due_date=task_in.due_date,
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Load relationships
    if new_task.assignee_id:
        await db.refresh(new_task, attribute_names=["assignee"])
    if new_task.sprint_id:
        await db.refresh(new_task, attribute_names=["sprint"])

    response = TaskResponse.model_validate(new_task)
    response.assignee_name = new_task.assignee.full_name if new_task.assignee else None
    response.sprint_title = new_task.sprint.title if new_task.sprint else None
    return response


@router.get("/sprints/{sprint_id}/tasks", response_model=list[TaskResponse])
async def list_tasks_by_sprint(
    sprint_id: int,
    status: Optional[str] = Query(None, description="Filter by status: todo, doing, done"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List all tasks in a sprint."""
    # Verify sprint exists
    sprint_result = await db.execute(
        select(Sprint).where(Sprint.sprint_id == sprint_id)
    )
    sprint = sprint_result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found",
        )

    # Verify access
    user_role = current_user.role.role_name.upper()
    if user_role == "STUDENT":
        if not await verify_team_member(db, sprint.team_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

    # Build query
    query = (
        select(Task)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.sprint),
        )
        .where(Task.sprint_id == sprint_id)
    )

    if status:
        query = query.where(Task.status == status.lower())

    result = await db.execute(query)
    tasks = result.scalars().all()

    responses = []
    for task in tasks:
        resp = TaskResponse.model_validate(task)
        resp.assignee_name = task.assignee.full_name if task.assignee else None
        resp.sprint_title = task.sprint.title if task.sprint else None
        responses.append(resp)

    return responses


@router.get("/sprints/{sprint_id}/board", response_model=TaskBoardResponse)
async def get_task_board(
    sprint_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get Task Board (Kanban view) grouped by status.
    Returns tasks organized into: todo, doing, done, backlog.
    """
    # Verify sprint exists
    sprint_result = await db.execute(
        select(Sprint).where(Sprint.sprint_id == sprint_id)
    )
    sprint = sprint_result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found",
        )

    # Verify access
    user_role = current_user.role.role_name.upper()
    if user_role == "STUDENT":
        if not await verify_team_member(db, sprint.team_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

    # Get all tasks
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.sprint),
        )
        .where(Task.sprint_id == sprint_id)
    )
    tasks = result.scalars().all()

    # Group by status
    board = TaskBoardResponse(
        todo=[],
        doing=[],
        done=[],
        backlog=[],
    )

    for task in tasks:
        task_resp = TaskResponse.model_validate(task)
        task_resp.assignee_name = task.assignee.full_name if task.assignee else None
        task_resp.sprint_title = task.sprint.title if task.sprint else None

        task_status = (task.status or "todo").lower()
        if task_status == "todo":
            board.todo.append(task_resp)
        elif task_status == "doing":
            board.doing.append(task_resp)
        elif task_status == "done":
            board.done.append(task_resp)
        else:
            board.backlog.append(task_resp)

    return board


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get Task details."""
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.assignee),
            selectinload(Task.sprint).selectinload(Sprint.team),
        )
        .where(Task.task_id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Verify access
    if task.sprint:
        user_role = current_user.role.role_name.upper()
        if user_role == "STUDENT":
            if not await verify_team_member(db, task.sprint.team_id, current_user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a member of this team",
                )

    response = TaskResponse.model_validate(task)
    response.assignee_name = task.assignee.full_name if task.assignee else None
    response.sprint_title = task.sprint.title if task.sprint else None
    return response


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update Task.
    Team members can update any task.
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.sprint))
        .where(Task.task_id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Verify team membership
    if task.sprint:
        if current_user.role.role_name.upper() == "STUDENT":
            if not await verify_team_member(db, task.sprint.team_id, current_user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a member of this team",
                )

    # Validate status
    if task_in.status and task_in.status not in ["todo", "doing", "done"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be: todo, doing, done",
        )

    # Validate priority
    if task_in.priority and task_in.priority not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid priority. Must be: low, medium, high",
        )

    # Verify new assignee is team member
    if task_in.assignee_id and task.sprint:
        if not await verify_team_member(db, task.sprint.team_id, task_in.assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a member of this team",
            )

    # Update fields
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    await db.refresh(task, attribute_names=["assignee", "sprint"])

    response = TaskResponse.model_validate(task)
    response.assignee_name = task.assignee.full_name if task.assignee else None
    response.sprint_title = task.sprint.title if task.sprint else None
    return response


@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Quick status update for drag-and-drop functionality.
    Team members can update task status.
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.sprint))
        .where(Task.task_id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Verify team membership
    if task.sprint:
        if current_user.role.role_name.upper() == "STUDENT":
            if not await verify_team_member(db, task.sprint.team_id, current_user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a member of this team",
                )

    # Validate status
    if status_update.status not in ["todo", "doing", "done"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be: todo, doing, done",
        )

    task.status = status_update.status
    await db.commit()
    await db.refresh(task)
    await db.refresh(task, attribute_names=["assignee", "sprint"])

    response = TaskResponse.model_validate(task)
    response.assignee_name = task.assignee.full_name if task.assignee else None
    response.sprint_title = task.sprint.title if task.sprint else None
    return response


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete Task.
    Team members can delete tasks.
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.sprint))
        .where(Task.task_id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Verify team membership
    if task.sprint:
        if current_user.role.role_name.upper() == "STUDENT":
            if not await verify_team_member(db, task.sprint.team_id, current_user.user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not a member of this team",
                )

    await db.delete(task)
    await db.commit()
    return None


# ==========================================
# STATISTICS ENDPOINTS
# ==========================================

@router.get("/sprints/{sprint_id}/statistics", response_model=TaskStatistics)
async def get_sprint_statistics(
    sprint_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get task statistics for a sprint."""
    # Verify sprint exists
    sprint_result = await db.execute(
        select(Sprint).where(Sprint.sprint_id == sprint_id)
    )
    sprint = sprint_result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sprint {sprint_id} not found",
        )

    # Verify access
    user_role = current_user.role.role_name.upper()
    if user_role == "STUDENT":
        if not await verify_team_member(db, sprint.team_id, current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this team",
            )

    # Get statistics
    result = await db.execute(
        select(
            func.count().label("total"),
            func.sum(func.cast(Task.status == "todo", Integer)).label("todo"),
            func.sum(func.cast(Task.status == "doing", Integer)).label("doing"),
            func.sum(func.cast(Task.status == "done", Integer)).label("done"),
        ).where(Task.sprint_id == sprint_id)
    )
    stats = result.one()

    total_tasks = stats.total or 0
    todo_count = stats.todo or 0
    doing_count = stats.doing or 0
    done_count = stats.done or 0

    completion_rate = (done_count / total_tasks * 100) if total_tasks > 0 else 0.0

    return TaskStatistics(
        total_tasks=total_tasks,
        todo_count=todo_count,
        doing_count=doing_count,
        done_count=done_count,
        completion_rate=round(completion_rate, 2),
    )
