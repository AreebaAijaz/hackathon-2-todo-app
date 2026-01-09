"""Tests for the Task model and validation functions."""

import pytest
from datetime import datetime

from src.models import Task, validate_title, validate_description, ValidationError


class TestTask:
    """Tests for the Task dataclass."""

    def test_task_creation_with_defaults(self) -> None:
        """Test creating a task with default values."""
        task = Task(title="Test task")

        assert task.title == "Test task"
        assert task.description == ""
        assert task.completed is False
        assert len(task.id) == 36  # UUID length
        assert isinstance(task.created_at, datetime)

    def test_task_creation_with_all_fields(self) -> None:
        """Test creating a task with all fields specified."""
        task = Task(
            title="Full task",
            description="A detailed description",
            completed=True,
        )

        assert task.title == "Full task"
        assert task.description == "A detailed description"
        assert task.completed is True

    def test_task_ids_are_unique(self) -> None:
        """Test that each task gets a unique ID."""
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        assert task1.id != task2.id


class TestValidateTitle:
    """Tests for the validate_title function."""

    def test_valid_title(self) -> None:
        """Test validation of a normal title."""
        result = validate_title("Buy groceries")
        assert result == "Buy groceries"

    def test_title_strips_whitespace(self) -> None:
        """Test that whitespace is stripped from title."""
        result = validate_title("  Trimmed title  ")
        assert result == "Trimmed title"

    def test_title_at_max_length(self) -> None:
        """Test title at exactly 100 characters."""
        title = "A" * 100
        result = validate_title(title)
        assert result == title

    def test_title_single_character(self) -> None:
        """Test minimum valid title (1 character)."""
        result = validate_title("A")
        assert result == "A"

    def test_empty_title_raises_error(self) -> None:
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Test that whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("   ")

    def test_title_too_long_raises_error(self) -> None:
        """Test that title over 100 characters raises ValidationError."""
        long_title = "A" * 101
        with pytest.raises(ValidationError, match="Title must be 100 characters or less"):
            validate_title(long_title)


class TestValidateDescription:
    """Tests for the validate_description function."""

    def test_valid_description(self) -> None:
        """Test validation of a normal description."""
        result = validate_description("A detailed description")
        assert result == "A detailed description"

    def test_empty_description_is_valid(self) -> None:
        """Test that empty description is valid."""
        result = validate_description("")
        assert result == ""

    def test_description_strips_whitespace(self) -> None:
        """Test that whitespace is stripped from description."""
        result = validate_description("  Trimmed  ")
        assert result == "Trimmed"

    def test_description_at_max_length(self) -> None:
        """Test description at exactly 500 characters."""
        desc = "A" * 500
        result = validate_description(desc)
        assert result == desc

    def test_description_too_long_raises_error(self) -> None:
        """Test that description over 500 characters raises ValidationError."""
        long_desc = "A" * 501
        with pytest.raises(ValidationError, match="Description must be 500 characters or less"):
            validate_description(long_desc)
