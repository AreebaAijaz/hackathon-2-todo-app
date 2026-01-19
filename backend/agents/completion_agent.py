"""Completion Agent - Handles task completion operations."""

from typing import Optional, List

from .base import BaseAgent, AgentResult
from mcp_server import (
    complete_task, list_tasks,
    CompleteTaskInput, ListTasksInput,
    TaskNotFoundError, UnauthorizedError,
)
from skills import (
    id_resolver, TaskReference,
    confirmation_generator, TaskInfo,
    error_handler,
)


class CompletionAgent(BaseAgent):
    """Agent for marking tasks as complete.

    Handles intents:
    - complete/done/finish: Mark a task as complete
    - check off: Mark a task as complete
    """

    name = "completion_agent"
    description = "Handles marking tasks as complete"
    available_tools = ["complete_task", "list_tasks"]

    # Intent mappings
    COMPLETION_INTENTS = [
        "complete", "done", "finish", "finished",
        "check", "mark", "tick", "crossed"
    ]

    def can_handle(self, intent: str, **kwargs) -> bool:
        """Check if this agent handles the given intent."""
        intent_lower = intent.lower()
        return any(i in intent_lower for i in self.COMPLETION_INTENTS)

    def execute(self, intent: str, **kwargs) -> AgentResult:
        """Execute the completion operation.

        Args:
            intent: The user's intent
            **kwargs: Additional parameters:
                - task_id: Explicit task ID to complete
                - user_input: Natural language reference to resolve

        Returns:
            AgentResult with completion outcome
        """
        try:
            task_id = kwargs.get("task_id")
            user_input = kwargs.get("user_input", "")

            # If no task_id, try to resolve from user input
            if not task_id and user_input:
                task_id = self._resolve_task_id(user_input)

            if not task_id:
                return AgentResult(
                    success=False,
                    message="Which task would you like to mark as complete? Please specify the task ID or name.",
                    error="No task_id resolved"
                )

            # Complete the task
            result = complete_task(CompleteTaskInput(
                user_id=self.user_id,
                task_id=task_id
            ))

            # Generate appropriate confirmation based on status
            task_info = TaskInfo(
                id=result.task_id,
                title=result.title
            )

            if result.status == "already_completed":
                message = confirmation_generator.execute("already_completed", task=task_info)
            else:
                message = confirmation_generator.execute("completed", task=task_info)

            return AgentResult(
                success=True,
                message=message,
                data={
                    "task_id": result.task_id,
                    "title": result.title,
                    "status": result.status
                },
                tool_used="complete_task"
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

    def _resolve_task_id(self, user_input: str) -> Optional[int]:
        """Resolve task ID from user input using ID resolver."""
        # Get user's pending tasks for matching
        result = list_tasks(ListTasksInput(
            user_id=self.user_id,
            status="pending"
        ))

        if not result.tasks:
            return None

        # Convert to TaskReference objects
        task_refs = [
            TaskReference(
                id=t.id,
                title=t.title,
                completed=t.completed
            )
            for t in result.tasks
        ]

        # Try to resolve
        resolved = id_resolver.execute(user_input, task_refs)

        return resolved.task_id
