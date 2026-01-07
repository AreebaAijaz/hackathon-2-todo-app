"""Data models for the Todo application."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Task:
    """Represents a todo task.

    Attributes:
        id: Unique identifier (UUID string).
        title: Task title (required, 1-100 characters).
        description: Task description (optional, max 500 characters).
        completed: Whether the task is complete.
        created_at: Timestamp when the task was created.
    """

    title: str
    description: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


def validate_title(title: str) -> str:
    """Validate and return the title.

    Args:
        title: The title to validate.

    Returns:
        The validated title (stripped of whitespace).

    Raises:
        ValidationError: If title is empty or exceeds 100 characters.
    """
    title = title.strip()
    if not title:
        raise ValidationError("Title cannot be empty")
    if len(title) > 100:
        raise ValidationError("Title must be 100 characters or less")
    return title


def validate_description(description: str) -> str:
    """Validate and return the description.

    Args:
        description: The description to validate.

    Returns:
        The validated description (stripped of whitespace).

    Raises:
        ValidationError: If description exceeds 500 characters.
    """
    description = description.strip()
    if len(description) > 500:
        raise ValidationError("Description must be 500 characters or less")
    return description
