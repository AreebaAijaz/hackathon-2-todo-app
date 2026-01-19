"""CRUD Agent - Handles create, update, and delete task operations."""

import re
from typing import Optional, List

from .base import BaseAgent, AgentResult
from mcp_server import (
    add_task, update_task, delete_task, list_tasks,
    AddTaskInput, UpdateTaskInput, DeleteTaskInput, ListTasksInput,
    TaskNotFoundError, UnauthorizedError,
)
from skills import (
    task_parser, ParsedTask,
    confirmation_generator, TaskInfo,
    error_handler,
    id_resolver, TaskReference,
)


class CRUDAgent(BaseAgent):
    """Agent for Create, Update, and Delete task operations.

    Handles intents:
    - add/create: Create a new task
    - update/edit: Modify an existing task
    - delete/remove: Delete a task
    """

    name = "crud_agent"
    description = "Handles task creation, updates, and deletion"
    available_tools = ["add_task", "update_task", "delete_task"]

    # Intent mappings
    CREATE_INTENTS = ["add", "create", "new", "make"]
    UPDATE_INTENTS = ["update", "edit", "change", "modify", "rename"]
    DELETE_INTENTS = ["delete", "remove", "cancel", "drop"]

    def can_handle(self, intent: str, **kwargs) -> bool:
        """Check if this agent handles the given intent."""
        intent_lower = intent.lower()
        all_intents = self.CREATE_INTENTS + self.UPDATE_INTENTS + self.DELETE_INTENTS
        return any(i in intent_lower for i in all_intents)

    def execute(self, intent: str, **kwargs) -> AgentResult:
        """Execute the CRUD operation based on intent.

        Args:
            intent: The user's intent (add, update, delete)
            **kwargs: Additional parameters:
                - user_input: Raw user input for parsing
                - task_id: Task ID for update/delete
                - title: New title for update
                - description: New description for update

        Returns:
            AgentResult with operation outcome
        """
        intent_lower = intent.lower()

        try:
            if any(i in intent_lower for i in self.CREATE_INTENTS):
                return self._handle_create(**kwargs)
            elif any(i in intent_lower for i in self.UPDATE_INTENTS):
                return self._handle_update(**kwargs)
            elif any(i in intent_lower for i in self.DELETE_INTENTS):
                return self._handle_delete(**kwargs)
            else:
                return AgentResult(
                    success=False,
                    message="I'm not sure what operation you want to perform.",
                    error="Unknown CRUD intent"
                )
        except TaskNotFoundError as e:
            error_response = error_handler.execute(error=e)
            return AgentResult(
                success=False,
                message=error_handler.format_response(error_response),
                error=str(e)
            )
        except UnauthorizedError as e:
            error_response = error_handler.execute(error=e)
            return AgentResult(
                success=False,
                message=error_handler.format_response(error_response),
                error=str(e)
            )
        except Exception as e:
            error_response = error_handler.execute(error=e)
            return AgentResult(
                success=False,
                message=error_handler.format_response(error_response),
                error=str(e)
            )

    def _handle_create(self, **kwargs) -> AgentResult:
        """Handle task creation."""
        user_input = kwargs.get("user_input", "")
        title = kwargs.get("title")
        description = kwargs.get("description")

        # Parse task from user input if title not provided
        if not title and user_input:
            parsed = task_parser.execute(user_input)
            if not parsed.has_title:
                return AgentResult(
                    success=False,
                    message="I couldn't understand the task title. Could you please specify what task you want to add?",
                    error="No title parsed"
                )
            title = parsed.title
            description = parsed.description or description

        if not title:
            return AgentResult(
                success=False,
                message="Please provide a title for the task.",
                error="No title provided"
            )

        # Create the task
        result = add_task(AddTaskInput(
            user_id=self.user_id,
            title=title,
            description=description or ""
        ))

        # Generate confirmation
        task_info = TaskInfo(
            id=result.task_id,
            title=result.title,
            description=description
        )
        message = confirmation_generator.execute("created", task=task_info)

        return AgentResult(
            success=True,
            message=message,
            data={
                "task_id": result.task_id,
                "title": result.title,
                "status": result.status
            },
            tool_used="add_task"
        )

    def _handle_update(self, **kwargs) -> AgentResult:
        """Handle task update."""
        task_id = kwargs.get("task_id")
        user_input = kwargs.get("user_input", "")
        title = kwargs.get("title")
        description = kwargs.get("description")
        completed = kwargs.get("completed")

        # Try to resolve task_id from user input if not provided
        if not task_id and user_input:
            task_id = self._resolve_task_id(user_input)

        if not task_id:
            return AgentResult(
                success=False,
                message="Which task would you like to update? Please specify the task ID or name.",
                error="No task_id provided"
            )

        # Update the task
        result = update_task(UpdateTaskInput(
            user_id=self.user_id,
            task_id=task_id,
            title=title,
            description=description,
            completed=completed
        ))

        # Generate confirmation
        task_info = TaskInfo(
            id=result.task_id,
            title=result.title
        )
        message = confirmation_generator.execute(
            "updated",
            task=task_info,
            changes=result.changes
        )

        return AgentResult(
            success=True,
            message=message,
            data={
                "task_id": result.task_id,
                "title": result.title,
                "changes": result.changes
            },
            tool_used="update_task"
        )

    def _resolve_task_id(self, user_input: str) -> Optional[int]:
        """Resolve task ID from user input."""
        # Try direct ID extraction first
        match = re.search(r'(?:task|todo|item)?\s*#?\s*(\d+)', user_input, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Try to resolve by name using ID resolver
        result = list_tasks(ListTasksInput(user_id=self.user_id, status="all"))
        if not result.tasks:
            return None

        task_refs = [
            TaskReference(id=t.id, title=t.title, completed=t.completed)
            for t in result.tasks
        ]

        resolved = id_resolver.execute(user_input, task_refs)
        return resolved.task_id

    def _handle_delete(self, **kwargs) -> AgentResult:
        """Handle task deletion."""
        task_id = kwargs.get("task_id")
        user_input = kwargs.get("user_input", "")

        # Try to resolve task_id from user input if not provided
        if not task_id and user_input:
            task_id = self._resolve_task_id(user_input)

        if not task_id:
            return AgentResult(
                success=False,
                message="Which task would you like to delete? Please specify the task ID or name.",
                error="No task_id provided"
            )

        # Delete the task
        result = delete_task(DeleteTaskInput(
            user_id=self.user_id,
            task_id=task_id
        ))

        # Generate confirmation
        task_info = TaskInfo(
            id=result.task_id,
            title=result.title
        )
        message = confirmation_generator.execute("deleted", task=task_info)

        return AgentResult(
            success=True,
            message=message,
            data={
                "task_id": result.task_id,
                "title": result.title
            },
            tool_used="delete_task"
        )
