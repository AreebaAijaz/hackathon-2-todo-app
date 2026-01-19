"""MCP Server - Task Management Tools for AI Agents."""

from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    MCPTools,
    TaskNotFoundError,
    UnauthorizedError,
)
from .schemas import (
    AddTaskInput,
    AddTaskOutput,
    ListTasksInput,
    ListTasksOutput,
    CompleteTaskInput,
    CompleteTaskOutput,
    DeleteTaskInput,
    DeleteTaskOutput,
    UpdateTaskInput,
    UpdateTaskOutput,
    TaskItem,
)

__all__ = [
    # Tools
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    "MCPTools",
    # Exceptions
    "TaskNotFoundError",
    "UnauthorizedError",
    # Schemas
    "AddTaskInput",
    "AddTaskOutput",
    "ListTasksInput",
    "ListTasksOutput",
    "CompleteTaskInput",
    "CompleteTaskOutput",
    "DeleteTaskInput",
    "DeleteTaskOutput",
    "UpdateTaskInput",
    "UpdateTaskOutput",
    "TaskItem",
]
