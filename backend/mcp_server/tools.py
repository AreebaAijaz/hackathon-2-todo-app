"""MCP Tools - Task Management Operations for AI Agents.

This module provides 5 MCP tools for task management:
1. add_task - Create a new task
2. list_tasks - List tasks with optional filtering
3. complete_task - Mark a task as complete
4. delete_task - Delete a task
5. update_task - Update task fields
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import select, Session

from database import get_session
from models import Task
from .schemas import (
    AddTaskInput, AddTaskOutput,
    ListTasksInput, ListTasksOutput,
    CompleteTaskInput, CompleteTaskOutput,
    DeleteTaskInput, DeleteTaskOutput,
    UpdateTaskInput, UpdateTaskOutput,
    TaskItem,
)


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    pass


class UnauthorizedError(Exception):
    """Raised when user doesn't own the task."""
    pass


def _get_task_by_id(session: Session, user_id: str, task_id: int) -> Task:
    """Helper to get a task by ID with ownership check."""
    stmt = select(Task).where(Task.id == task_id)
    task = session.exec(stmt).first()

    if not task:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")

    if task.user_id != user_id:
        raise UnauthorizedError(f"User {user_id} does not own task {task_id}")

    return task


def _task_to_item(task: Task) -> TaskItem:
    """Convert Task model to TaskItem schema."""
    return TaskItem(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
    )


# ============== MCP Tool 1: add_task ==============

def add_task(input: AddTaskInput) -> AddTaskOutput:
    """Create a new task for a user.

    Args:
        input: AddTaskInput with user_id, title, and optional description

    Returns:
        AddTaskOutput with task_id, status, and title
    """
    with next(get_session()) as session:
        task = Task(
            user_id=input.user_id,
            title=input.title,
            description=input.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return AddTaskOutput(
            task_id=task.id,
            status="created",
            title=task.title,
        )


# ============== MCP Tool 2: list_tasks ==============

def list_tasks(input: ListTasksInput) -> ListTasksOutput:
    """List tasks for a user with optional status filter.

    Args:
        input: ListTasksInput with user_id and status filter

    Returns:
        ListTasksOutput with tasks array, count, and filter applied
    """
    with next(get_session()) as session:
        stmt = select(Task).where(Task.user_id == input.user_id)

        # Apply status filter
        if input.status == "pending":
            stmt = stmt.where(Task.completed == False)
        elif input.status == "completed":
            stmt = stmt.where(Task.completed == True)
        # "all" = no additional filter

        # Order by created_at descending (newest first)
        stmt = stmt.order_by(Task.created_at.desc())

        tasks = session.exec(stmt).all()
        task_items = [_task_to_item(task) for task in tasks]

        return ListTasksOutput(
            tasks=task_items,
            count=len(task_items),
            filter_applied=input.status,
        )


# ============== MCP Tool 3: complete_task ==============

def complete_task(input: CompleteTaskInput) -> CompleteTaskOutput:
    """Mark a task as complete.

    Args:
        input: CompleteTaskInput with user_id and task_id

    Returns:
        CompleteTaskOutput with task_id, status, and title

    Raises:
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own the task
    """
    with next(get_session()) as session:
        task = _get_task_by_id(session, input.user_id, input.task_id)

        # Check if already completed
        if task.completed:
            return CompleteTaskOutput(
                task_id=task.id,
                status="already_completed",
                title=task.title,
            )

        # Mark as complete
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        return CompleteTaskOutput(
            task_id=task.id,
            status="completed",
            title=task.title,
        )


# ============== MCP Tool 4: delete_task ==============

def delete_task(input: DeleteTaskInput) -> DeleteTaskOutput:
    """Delete a task.

    Args:
        input: DeleteTaskInput with user_id and task_id

    Returns:
        DeleteTaskOutput with task_id, status, and title

    Raises:
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own the task
    """
    with next(get_session()) as session:
        task = _get_task_by_id(session, input.user_id, input.task_id)
        title = task.title
        task_id = task.id

        session.delete(task)
        session.commit()

        return DeleteTaskOutput(
            task_id=task_id,
            status="deleted",
            title=title,
        )


# ============== MCP Tool 5: update_task ==============

def update_task(input: UpdateTaskInput) -> UpdateTaskOutput:
    """Update a task's fields.

    Args:
        input: UpdateTaskInput with user_id, task_id, and optional fields to update

    Returns:
        UpdateTaskOutput with task_id, status, title, and list of changes

    Raises:
        TaskNotFoundError: If task doesn't exist
        UnauthorizedError: If user doesn't own the task
    """
    with next(get_session()) as session:
        task = _get_task_by_id(session, input.user_id, input.task_id)

        changes = []

        if input.title is not None:
            task.title = input.title
            changes.append("title")

        if input.description is not None:
            task.description = input.description
            changes.append("description")

        if input.completed is not None:
            task.completed = input.completed
            changes.append("completed")

        if changes:
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

        return UpdateTaskOutput(
            task_id=task.id,
            status="updated",
            title=task.title,
            changes=changes,
        )


# ============== MCP Tools Registry ==============

class MCPTools:
    """Registry of all MCP tools with their definitions for OpenAI function calling."""

    @staticmethod
    def get_tool_definitions() -> List[dict]:
        """Get OpenAI-compatible tool definitions for all MCP tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user. Use this when the user wants to add a new todo item.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title/name"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description with more details"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List the user's tasks. Can filter by status: 'all', 'pending', or 'completed'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter tasks by status. Default is 'all'."
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as complete/done. Use this when the user wants to finish or check off a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to mark as complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently. Use this when the user wants to remove a task from their list.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title, description, or completion status.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the task (optional)"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the task (optional)"
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "New completion status (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]

    @staticmethod
    def execute_tool(tool_name: str, user_id: str, arguments: dict):
        """Execute an MCP tool by name with the given arguments.

        Args:
            tool_name: Name of the tool to execute
            user_id: User ID to pass to the tool
            arguments: Tool arguments from OpenAI function call

        Returns:
            Tool output object

        Raises:
            ValueError: If tool_name is unknown
        """
        if tool_name == "add_task":
            return add_task(AddTaskInput(
                user_id=user_id,
                title=arguments.get("title", ""),
                description=arguments.get("description", ""),
            ))
        elif tool_name == "list_tasks":
            return list_tasks(ListTasksInput(
                user_id=user_id,
                status=arguments.get("status", "all"),
            ))
        elif tool_name == "complete_task":
            return complete_task(CompleteTaskInput(
                user_id=user_id,
                task_id=arguments.get("task_id"),
            ))
        elif tool_name == "delete_task":
            return delete_task(DeleteTaskInput(
                user_id=user_id,
                task_id=arguments.get("task_id"),
            ))
        elif tool_name == "update_task":
            return update_task(UpdateTaskInput(
                user_id=user_id,
                task_id=arguments.get("task_id"),
                title=arguments.get("title"),
                description=arguments.get("description"),
                completed=arguments.get("completed"),
            ))
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
