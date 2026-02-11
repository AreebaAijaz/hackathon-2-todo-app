"""Task CRUD routes for the Todo API — Phase 5B Event-Driven."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, case, func, text as sa_text
from sqlalchemy import Text

from database import get_session
from models import Task
from auth.dependencies import get_current_user
from events.publisher import publish_task_event, publish_reminder_event
from schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    MessageResponse,
    BulkUpdateRequest,
    BulkUpdateResponse,
    TagsResponse,
)

router = APIRouter(prefix="/api", tags=["tasks"])

# Priority sort order mapping (urgent first)
PRIORITY_ORDER = {"urgent": 0, "high": 1, "medium": 2, "low": 3}


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    # Filtering
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    overdue: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    # Sorting
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
):
    """List tasks with optional filtering, sorting, and full-text search.

    Query Parameters:
        status: Filter by completion status (all/pending/completed)
        priority: Filter by priority, comma-separated (e.g., high,urgent)
        tags: Filter by tags, comma-separated with AND logic (e.g., work,urgent)
        due_before: Tasks with due_date before this datetime
        due_after: Tasks with due_date after this datetime
        overdue: If true, only overdue tasks (due_date < now AND not completed)
        search: Full-text search query on title and description
        sort_by: Sort field (created_at/due_date/priority/title)
        sort_dir: Sort direction (asc/desc)
    """
    statement = select(Task).where(Task.user_id == user_id)

    # Status filter
    if status_filter == "pending":
        statement = statement.where(Task.completed == False)
    elif status_filter == "completed":
        statement = statement.where(Task.completed == True)

    # Priority filter (comma-separated, OR logic within)
    if priority:
        priorities = [p.strip() for p in priority.split(",")]
        valid = {"low", "medium", "high", "urgent"}
        priorities = [p for p in priorities if p in valid]
        if priorities:
            statement = statement.where(Task.priority.in_(priorities))

    # Tag filter (comma-separated, AND logic — task must have ALL specified tags)
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_list:
            statement = statement.where(Task.tags.contains(tag_list))

    # Due date range filters
    if due_after:
        statement = statement.where(Task.due_date >= due_after)
    if due_before:
        statement = statement.where(Task.due_date <= due_before)

    # Overdue filter
    if overdue is True:
        statement = statement.where(
            Task.due_date < func.now(),
            Task.completed == False,
            Task.due_date.isnot(None),
        )

    # Full-text search using tsvector
    if search and search.strip():
        ts_query = func.plainto_tsquery("english", search.strip())
        statement = statement.where(
            Task.search_vector.op("@@")(ts_query)
        )
        # When searching, default sort by relevance unless explicitly overridden
        if sort_by == "created_at":  # default wasn't changed by user
            statement = statement.order_by(
                func.ts_rank(Task.search_vector, ts_query).desc()
            )
            tasks = session.exec(statement).all()
            return tasks

    # Sorting
    if sort_by == "priority":
        priority_case = case(
            (Task.priority == "urgent", 0),
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
        )
        order_col = priority_case.asc() if sort_dir == "asc" else priority_case.desc()
    elif sort_by == "due_date":
        # NULLS LAST regardless of sort direction
        if sort_dir == "asc":
            order_col = Task.due_date.asc().nullslast()
        else:
            order_col = Task.due_date.desc().nullslast()
    elif sort_by == "title":
        order_col = Task.title.asc() if sort_dir == "asc" else Task.title.desc()
    else:  # created_at (default)
        order_col = Task.created_at.asc() if sort_dir == "asc" else Task.created_at.desc()

    statement = statement.order_by(order_col)
    tasks = session.exec(statement).all()
    return tasks


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task with optional priority, tags, due date, and recurring pattern."""
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tags=task_data.tags,
        due_date=task_data.due_date,
        recurring_pattern=task_data.recurring_pattern,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish events (fire-and-forget)
    await publish_task_event("task.created", task, user_id)
    await publish_reminder_event(task, user_id)

    return task


@router.get("/tasks/tags", response_model=TagsResponse)
async def list_user_tags(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all unique tags used by the authenticated user, for autocomplete."""
    result = session.exec(
        sa_text(
            "SELECT DISTINCT unnest(tags) as tag FROM tasks WHERE user_id = :uid ORDER BY tag"
        ).bindparams(uid=user_id)
    )
    tags_list = [row[0] for row in result]
    return TagsResponse(tags=tags_list, count=len(tags_list))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific task by ID."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update a task's fields including priority, tags, due date, and recurring pattern."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.tags is not None:
        task.tags = task_data.tags
    # due_date: explicitly check if field was provided (allow setting to None to clear)
    if "due_date" in task_data.model_fields_set:
        task.due_date = task_data.due_date
    if task_data.recurring_pattern is not None:
        task.recurring_pattern = task_data.recurring_pattern

    due_date_changed = "due_date" in task_data.model_fields_set
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish events (fire-and-forget)
    await publish_task_event("task.updated", task, user_id)
    if due_date_changed:
        await publish_reminder_event(task, user_id)

    return task


@router.delete("/tasks/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a task."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Capture task data before deletion for event publishing
    await publish_task_event("task.deleted", task, user_id)

    session.delete(task)
    session.commit()
    return MessageResponse(message="Task deleted successfully")


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle a task's completion status."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish event (fire-and-forget)
    event_type = "task.completed" if task.completed else "task.updated"
    await publish_task_event(event_type, task, user_id)

    return task


@router.patch("/tasks/bulk", response_model=BulkUpdateResponse)
async def bulk_update_tasks(
    bulk_data: BulkUpdateRequest,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Apply operations to multiple tasks at once.

    Supports: set priority, add/remove tags, set due_date, set recurring_pattern.
    All specified task_ids must belong to the authenticated user.
    """
    # Fetch all specified tasks owned by user
    statement = select(Task).where(
        Task.id.in_(bulk_data.task_ids),
        Task.user_id == user_id,
    )
    tasks = session.exec(statement).all()

    # Verify all task IDs were found
    found_ids = {t.id for t in tasks}
    missing = set(bulk_data.task_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tasks not found or not owned: {sorted(missing)}",
        )

    ops = bulk_data.operations
    updated_ids = []

    for task in tasks:
        changed = False

        if ops.priority is not None:
            task.priority = ops.priority
            changed = True

        if ops.add_tags:
            current_tags = set(task.tags or [])
            current_tags.update(ops.add_tags)
            if len(current_tags) > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task {task.id} would exceed 10 tags after adding",
                )
            task.tags = sorted(current_tags)
            changed = True

        if ops.remove_tags:
            current_tags = set(task.tags or [])
            current_tags -= set(ops.remove_tags)
            task.tags = sorted(current_tags)
            changed = True

        if "due_date" in ops.model_fields_set:
            task.due_date = ops.due_date
            changed = True

        if ops.recurring_pattern is not None:
            task.recurring_pattern = ops.recurring_pattern
            changed = True

        if changed:
            task.updated_at = datetime.utcnow()
            session.add(task)
            updated_ids.append(task.id)

    session.commit()
    return BulkUpdateResponse(
        updated_count=len(updated_ids),
        task_ids=sorted(updated_ids),
    )
