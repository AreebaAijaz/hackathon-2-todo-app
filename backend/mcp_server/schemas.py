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
    priority: str = "medium"
    tags: List[str] = []
    due_date: Optional[datetime] = None
    recurring_pattern: str = "none"
    is_overdue: bool = False


# ============== add_task ==============

class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., description="The user ID who owns the task")
    title: str = Field(..., description="The task title", min_length=1, max_length=200)
    description: str = Field(default="", description="Optional task description", max_length=500)
    priority: str = Field(default="medium", description="Priority level: low, medium, high, urgent")
    tags: List[str] = Field(default_factory=list, description="List of tags for the task")
    due_date: Optional[str] = Field(default=None, description="Due date in ISO 8601 format")
    recurring_pattern: str = Field(default="none", description="Recurring pattern: none, daily, weekly, monthly")


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
    priority: Optional[str] = Field(default=None, description="Filter by priority (comma-separated): low, medium, high, urgent")
    tags: Optional[str] = Field(default=None, description="Filter by tags (comma-separated, AND logic)")
    overdue: Optional[bool] = Field(default=None, description="If true, only show overdue tasks")
    search: Optional[str] = Field(default=None, description="Full-text search query")
    sort_by: str = Field(default="created_at", description="Sort field: created_at, due_date, priority, title")


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
    priority: Optional[str] = Field(default=None, description="New priority: low, medium, high, urgent")
    tags: Optional[List[str]] = Field(default=None, description="New tags list (replaces existing)")
    due_date: Optional[str] = Field(default=None, description="New due date in ISO 8601 format, or empty string to clear")
    recurring_pattern: Optional[str] = Field(default=None, description="New recurring pattern: none, daily, weekly, monthly")


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool."""
    task_id: int
    status: Literal["updated"] = "updated"
    title: str
    changes: List[str]  # List of fields that were updated
