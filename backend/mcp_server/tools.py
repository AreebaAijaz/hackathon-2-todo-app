"""MCP Tools - Task Management Operations for AI Agents.

This module provides 5 MCP tools for task management:
1. add_task - Create a new task
2. list_tasks - List tasks with optional filtering
3. complete_task - Mark a task as complete
4. delete_task - Delete a task
5. update_task - Update task fields
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import select, Session, case, func

from database import get_session
from models import Task
from events.publisher import publish_task_event_sync, publish_reminder_event_sync
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
    is_overdue = False
    if task.due_date and not task.completed:
        due = task.due_date if task.due_date.tzinfo else task.due_date.replace(tzinfo=timezone.utc)
        is_overdue = due < datetime.now(timezone.utc)
    return TaskItem(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=task.created_at,
        priority=task.priority,
        tags=task.tags or [],
        due_date=task.due_date,
        recurring_pattern=task.recurring_pattern,
        is_overdue=is_overdue,
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
        due_date_parsed = None
        if input.due_date:
            try:
                due_date_parsed = datetime.fromisoformat(input.due_date.replace("Z", "+00:00"))
            except ValueError:
                pass

        task = Task(
            user_id=input.user_id,
            title=input.title,
            description=input.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=input.priority if input.priority in ("low", "medium", "high", "urgent") else "medium",
            tags=[t.strip().lower() for t in input.tags][:10] if input.tags else [],
            due_date=due_date_parsed,
            recurring_pattern=input.recurring_pattern if input.recurring_pattern in ("none", "daily", "weekly", "monthly") else "none",
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Publish events (fire-and-forget)
        publish_task_event_sync("task.created", task, input.user_id)
        publish_reminder_event_sync(task, input.user_id)

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

        # Priority filter
        if input.priority:
            priorities = [p.strip() for p in input.priority.split(",")]
            valid = {"low", "medium", "high", "urgent"}
            priorities = [p for p in priorities if p in valid]
            if priorities:
                stmt = stmt.where(Task.priority.in_(priorities))

        # Tag filter (AND logic)
        if input.tags:
            tag_list = [t.strip().lower() for t in input.tags.split(",") if t.strip()]
            if tag_list:
                stmt = stmt.where(Task.tags.contains(tag_list))

        # Overdue filter
        if input.overdue is True:
            stmt = stmt.where(
                Task.due_date < func.now(),
                Task.completed == False,
                Task.due_date.isnot(None),
            )

        # Full-text search
        if input.search and input.search.strip():
            ts_query = func.plainto_tsquery("english", input.search.strip())
            stmt = stmt.where(Task.search_vector.op("@@")(ts_query))

        # Sorting
        if input.sort_by == "priority":
            priority_case = case(
                (Task.priority == "urgent", 0),
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
            )
            stmt = stmt.order_by(priority_case.asc())
        elif input.sort_by == "due_date":
            stmt = stmt.order_by(Task.due_date.asc().nullslast())
        elif input.sort_by == "title":
            stmt = stmt.order_by(Task.title.asc())
        else:
            stmt = stmt.order_by(Task.created_at.desc())

        tasks = session.exec(stmt).all()
        task_items = [_task_to_item(task) for task in tasks]

        filter_desc = input.status
        if input.priority:
            filter_desc += f", priority={input.priority}"
        if input.tags:
            filter_desc += f", tags={input.tags}"
        if input.overdue:
            filter_desc += ", overdue"
        if input.search:
            filter_desc += f", search={input.search}"

        return ListTasksOutput(
            tasks=task_items,
            count=len(task_items),
            filter_applied=filter_desc,
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

        # Publish event (fire-and-forget)
        publish_task_event_sync("task.completed", task, input.user_id)

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

        # Publish event before deletion (fire-and-forget)
        publish_task_event_sync("task.deleted", task, input.user_id)

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

        if input.priority is not None and input.priority in ("low", "medium", "high", "urgent"):
            task.priority = input.priority
            changes.append("priority")

        if input.tags is not None:
            task.tags = [t.strip().lower() for t in input.tags][:10]
            changes.append("tags")

        if input.due_date is not None:
            if input.due_date == "":
                task.due_date = None
            else:
                try:
                    task.due_date = datetime.fromisoformat(input.due_date.replace("Z", "+00:00"))
                except ValueError:
                    pass
            changes.append("due_date")

        if input.recurring_pattern is not None and input.recurring_pattern in ("none", "daily", "weekly", "monthly"):
            task.recurring_pattern = input.recurring_pattern
            changes.append("recurring_pattern")

        if changes:
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            # Publish events (fire-and-forget)
            publish_task_event_sync("task.updated", task, input.user_id)
            if "due_date" in changes:
                publish_reminder_event_sync(task, input.user_id)

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
                    "description": "Create a new task for the user. Use this when the user wants to add a new todo item. Supports priority, tags, due dates, and recurring patterns.",
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
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Task priority level. Default is 'medium'."
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags to categorize the task (e.g., ['work', 'urgent'])"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in ISO 8601 format (e.g., '2026-02-15T17:00:00Z')"
                            },
                            "recurring_pattern": {
                                "type": "string",
                                "enum": ["none", "daily", "weekly", "monthly"],
                                "description": "Recurring pattern. Default is 'none'."
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
                    "description": "List the user's tasks with optional filtering and sorting. Supports status, priority, tags, overdue, and full-text search filters.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter tasks by status. Default is 'all'."
                            },
                            "priority": {
                                "type": "string",
                                "description": "Filter by priority, comma-separated (e.g., 'high,urgent')"
                            },
                            "tags": {
                                "type": "string",
                                "description": "Filter by tags, comma-separated with AND logic (e.g., 'work,urgent')"
                            },
                            "overdue": {
                                "type": "boolean",
                                "description": "If true, only show overdue tasks (past due date and not completed)"
                            },
                            "search": {
                                "type": "string",
                                "description": "Full-text search query on task titles and descriptions"
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": ["created_at", "due_date", "priority", "title"],
                                "description": "Sort field. Default is 'created_at'."
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
                    "description": "Update a task's fields including title, description, priority, tags, due date, and recurring pattern.",
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
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "New priority level (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New tags list, replaces existing (optional)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "New due date in ISO 8601 format, or empty string to clear (optional)"
                            },
                            "recurring_pattern": {
                                "type": "string",
                                "enum": ["none", "daily", "weekly", "monthly"],
                                "description": "New recurring pattern (optional)"
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
                priority=arguments.get("priority", "medium"),
                tags=arguments.get("tags", []),
                due_date=arguments.get("due_date"),
                recurring_pattern=arguments.get("recurring_pattern", "none"),
            ))
        elif tool_name == "list_tasks":
            return list_tasks(ListTasksInput(
                user_id=user_id,
                status=arguments.get("status", "all"),
                priority=arguments.get("priority"),
                tags=arguments.get("tags"),
                overdue=arguments.get("overdue"),
                search=arguments.get("search"),
                sort_by=arguments.get("sort_by", "created_at"),
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
                priority=arguments.get("priority"),
                tags=arguments.get("tags"),
                due_date=arguments.get("due_date"),
                recurring_pattern=arguments.get("recurring_pattern"),
            ))
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
