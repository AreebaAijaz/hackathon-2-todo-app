"""Query Agent - Handles task listing and filtering operations."""

from typing import List, Optional

from .base import BaseAgent, AgentResult
from mcp_server import list_tasks, ListTasksInput
from skills import (
    filter_mapper,
    confirmation_generator, TaskInfo,
    error_handler,
)


class QueryAgent(BaseAgent):
    """Agent for querying and listing tasks.

    Handles intents:
    - list/show: Display tasks
    - filter: Filter by status (pending, completed, all)
    - count: Get task counts
    """

    name = "query_agent"
    description = "Handles task listing and filtering"
    available_tools = ["list_tasks"]

    # Intent mappings
    QUERY_INTENTS = [
        "list", "show", "display", "get", "view", "see",
        "what", "how many", "count", "tasks", "todos",
        "pending", "completed", "done", "remaining"
    ]

    def can_handle(self, intent: str, **kwargs) -> bool:
        """Check if this agent handles the given intent."""
        intent_lower = intent.lower()
        return any(i in intent_lower for i in self.QUERY_INTENTS)

    def execute(self, intent: str, **kwargs) -> AgentResult:
        """Execute the query operation.

        Args:
            intent: The user's intent
            **kwargs: Additional parameters:
                - user_input: Raw user input for filter parsing
                - status: Explicit status filter (all/pending/completed)

        Returns:
            AgentResult with task list
        """
        try:
            user_input = kwargs.get("user_input", intent)
            explicit_status = kwargs.get("status")

            # Determine filter from user input or explicit status
            if explicit_status:
                status = explicit_status
            else:
                filter_params = filter_mapper.execute(user_input)
                status = filter_params.status

            # Execute the query
            result = list_tasks(ListTasksInput(
                user_id=self.user_id,
                status=status
            ))

            # Convert to TaskInfo objects for confirmation
            task_infos = [
                TaskInfo(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    completed=t.completed
                )
                for t in result.tasks
            ]

            # Generate summary message
            message = confirmation_generator.execute(
                "listed",
                tasks=task_infos,
                filter_applied=result.filter_applied
            )

            # Build detailed task list for response
            task_list = self._format_task_list(result.tasks, result.filter_applied)
            if task_list:
                message = f"{message}\n\n{task_list}"

            return AgentResult(
                success=True,
                message=message,
                data={
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "completed": t.completed
                        }
                        for t in result.tasks
                    ],
                    "count": result.count,
                    "filter": result.filter_applied
                },
                tool_used="list_tasks"
            )

        except Exception as e:
            error_response = error_handler.execute(error=e)
            return AgentResult(
                success=False,
                message=error_handler.format_response(error_response),
                error=str(e)
            )

    def _format_task_list(self, tasks: List, filter_applied: str) -> str:
        """Format tasks into a readable list."""
        if not tasks:
            return ""

        lines = []
        for task in tasks:
            status_icon = "[x]" if task.completed else "[ ]"
            line = f"{status_icon} {task.title}"
            if task.description:
                line += f" - {task.description}"
            lines.append(line)

        return "\n".join(lines)
