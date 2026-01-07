"""In-memory storage layer for todo tasks."""

from src.models import Task, validate_title, validate_description, ValidationError


class TaskNotFoundError(Exception):
    """Raised when a task is not found by ID."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class TaskStorage:
    """In-memory storage for todo tasks.

    Provides CRUD operations for managing tasks in memory.
    Data is lost when the application exits.
    """

    def __init__(self) -> None:
        """Initialize empty task storage."""
        self._tasks: list[Task] = []

    def add_task(self, title: str, description: str = "") -> Task:
        """Create and store a new task.

        Args:
            title: Task title (required, 1-100 characters).
            description: Task description (optional, max 500 characters).

        Returns:
            The newly created Task.

        Raises:
            ValidationError: If title or description is invalid.
        """
        validated_title = validate_title(title)
        validated_description = validate_description(description)

        task = Task(title=validated_title, description=validated_description)
        self._tasks.append(task)
        return task

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks.

        Returns:
            List of all tasks (may be empty).
        """
        return list(self._tasks)

    def get_task_by_id(self, task_id: str) -> Task | None:
        """Retrieve a task by its ID.

        Args:
            task_id: The UUID of the task to find.

        Returns:
            The Task if found, None otherwise.
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update a task's title and/or description.

        Args:
            task_id: The UUID of the task to update.
            title: New title (None to keep current).
            description: New description (None to keep current).

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist.
            ValidationError: If new title or description is invalid.
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        if title is not None:
            task.title = validate_title(title)

        if description is not None:
            task.description = validate_description(description)

        return task

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by its ID.

        Args:
            task_id: The UUID of the task to delete.

        Returns:
            True if task was deleted.

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist.
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        self._tasks.remove(task)
        return True

    def toggle_complete(self, task_id: str) -> Task:
        """Toggle a task's completion status.

        Args:
            task_id: The UUID of the task to toggle.

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If task with given ID doesn't exist.
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        task.completed = not task.completed
        return task
