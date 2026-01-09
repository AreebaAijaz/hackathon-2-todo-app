"""Task CRUD routes for the Todo API."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models import Task
from auth.dependencies import get_current_user
from schemas import TaskCreate, TaskUpdate, TaskResponse, MessageResponse

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all tasks for the authenticated user.

    Returns:
        List of tasks belonging to the current user.
    """
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return tasks


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new task for the authenticated user.

    Args:
        task_data: The task data (title, description).

    Returns:
        The newly created task.
    """
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific task by ID.

    Args:
        task_id: The task ID.

    Returns:
        The task if found and owned by the user.

    Raises:
        404: If task not found or not owned by user.
    """
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
    """Update a task's title and/or description.

    Args:
        task_id: The task ID.
        task_data: The fields to update.

    Returns:
        The updated task.

    Raises:
        404: If task not found or not owned by user.
    """
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

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/tasks/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a task.

    Args:
        task_id: The task ID.

    Returns:
        Confirmation message.

    Raises:
        404: If task not found or not owned by user.
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    session.delete(task)
    session.commit()
    return MessageResponse(message="Task deleted successfully")


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Toggle a task's completion status.

    Args:
        task_id: The task ID.

    Returns:
        The updated task with toggled completion status.

    Raises:
        404: If task not found or not owned by user.
    """
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
    return task
