"""Confirmation Generator Skill - Generate human-friendly confirmations."""

from typing import Literal, Optional, List
from dataclasses import dataclass

from .base import BaseSkill


@dataclass
class TaskInfo:
    """Task information for confirmation generation."""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False


class ConfirmationGeneratorSkill(BaseSkill):
    """Generate human-friendly confirmation messages for task operations.

    Provides natural, conversational confirmations for:
    - Task creation
    - Task completion
    - Task deletion
    - Task updates
    - Task listing
    """

    name = "confirmation_generator"
    description = "Generates human-friendly confirmation messages"

    def execute(
        self,
        action: Literal["created", "completed", "deleted", "updated", "listed", "already_completed"],
        task: Optional[TaskInfo] = None,
        tasks: Optional[List[TaskInfo]] = None,
        changes: Optional[List[str]] = None,
        filter_applied: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a confirmation message for a task operation.

        Args:
            action: The action that was performed
            task: Task info for single-task operations
            tasks: List of tasks for list operations
            changes: List of fields that were changed (for updates)
            filter_applied: Filter used (for listing)

        Returns:
            Human-friendly confirmation message
        """
        if action == "created":
            return self._confirm_created(task)
        elif action == "completed":
            return self._confirm_completed(task)
        elif action == "already_completed":
            return self._confirm_already_completed(task)
        elif action == "deleted":
            return self._confirm_deleted(task)
        elif action == "updated":
            return self._confirm_updated(task, changes)
        elif action == "listed":
            return self._confirm_listed(tasks, filter_applied)
        else:
            return "Operation completed."

    def _confirm_created(self, task: Optional[TaskInfo]) -> str:
        """Generate confirmation for task creation."""
        if not task:
            return "Task created successfully."

        msg = f"I've added \"{task.title}\" to your tasks."
        if task.description:
            msg += f" ({task.description})"
        return msg

    def _confirm_completed(self, task: Optional[TaskInfo]) -> str:
        """Generate confirmation for task completion."""
        if not task:
            return "Task marked as complete."

        return f"Nice work! \"{task.title}\" is now complete."

    def _confirm_already_completed(self, task: Optional[TaskInfo]) -> str:
        """Generate message when task is already completed."""
        if not task:
            return "This task is already completed."

        return f"\"{task.title}\" was already marked as complete."

    def _confirm_deleted(self, task: Optional[TaskInfo]) -> str:
        """Generate confirmation for task deletion."""
        if not task:
            return "Task deleted."

        return f"I've removed \"{task.title}\" from your tasks."

    def _confirm_updated(self, task: Optional[TaskInfo], changes: Optional[List[str]]) -> str:
        """Generate confirmation for task update."""
        if not task:
            return "Task updated successfully."

        if not changes:
            return f"No changes were made to \"{task.title}\"."

        change_text = self._format_changes(changes)
        return f"I've updated the {change_text} for \"{task.title}\"."

    def _format_changes(self, changes: List[str]) -> str:
        """Format list of changes into readable text."""
        if len(changes) == 1:
            return changes[0]
        elif len(changes) == 2:
            return f"{changes[0]} and {changes[1]}"
        else:
            return ", ".join(changes[:-1]) + f", and {changes[-1]}"

    def _confirm_listed(self, tasks: Optional[List[TaskInfo]], filter_applied: Optional[str]) -> str:
        """Generate summary for task listing."""
        if not tasks:
            if filter_applied == "completed":
                return "You haven't completed any tasks yet."
            elif filter_applied == "pending":
                return "Great news! You have no pending tasks."
            else:
                return "You don't have any tasks yet. Would you like to add one?"

        count = len(tasks)
        pending = sum(1 for t in tasks if not t.completed)
        completed = count - pending

        if filter_applied == "pending":
            if count == 1:
                return f"You have 1 pending task: \"{tasks[0].title}\""
            return f"You have {count} pending tasks."
        elif filter_applied == "completed":
            if count == 1:
                return f"You've completed 1 task: \"{tasks[0].title}\""
            return f"You've completed {count} tasks."
        else:
            # All tasks
            if count == 1:
                status = "completed" if tasks[0].completed else "pending"
                return f"You have 1 task ({status}): \"{tasks[0].title}\""

            parts = []
            if pending > 0:
                parts.append(f"{pending} pending")
            if completed > 0:
                parts.append(f"{completed} completed")

            return f"You have {count} tasks ({', '.join(parts)})."


# Singleton instance
confirmation_generator = ConfirmationGeneratorSkill()
