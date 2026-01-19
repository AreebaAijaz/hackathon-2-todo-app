"""Pydantic schemas for MCP Tool inputs and outputs."""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ============== Task Item Schema ==============

class TaskItem(BaseModel):
    """Represents a task item in responses."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime


# ============== add_task ==============

class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., description="The user ID who owns the task")
    title: str = Field(..., description="The task title", min_length=1, max_length=200)
    description: str = Field(default="", description="Optional task description", max_length=500)


class AddTaskOutput(BaseModel):
    """Output schema for add_task tool."""
    task_id: int
    status: Literal["created"] = "created"
    title: str


# ============== list_tasks ==============

class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., description="The user ID to list tasks for")
    status: Literal["all", "pending", "completed"] = Field(
        default="all",
        description="Filter tasks by status: 'all', 'pending', or 'completed'"
    )


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool."""
    tasks: List[TaskItem]
    count: int
    filter_applied: str


# ============== complete_task ==============

class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    user_id: str = Field(..., description="The user ID who owns the task")
    task_id: int = Field(..., description="The task ID to mark as complete")


class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task tool."""
    task_id: int
    status: Literal["completed", "already_completed"]
    title: str


# ============== delete_task ==============

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., description="The user ID who owns the task")
    task_id: int = Field(..., description="The task ID to delete")


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""
    task_id: int
    status: Literal["deleted"] = "deleted"
    title: str


# ============== update_task ==============

class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="The user ID who owns the task")
    task_id: int = Field(..., description="The task ID to update")
    title: Optional[str] = Field(default=None, description="New title (optional)", max_length=200)
    description: Optional[str] = Field(default=None, description="New description (optional)", max_length=500)
    completed: Optional[bool] = Field(default=None, description="New completed status (optional)")


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool."""
    task_id: int
    status: Literal["updated"] = "updated"
    title: str
    changes: List[str]  # List of fields that were updated
