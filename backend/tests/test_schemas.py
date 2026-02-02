"""Test Pydantic schemas for request/response validation."""

import pytest
from pydantic import ValidationError
from datetime import datetime

from schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    ErrorResponse,
    MessageResponse,
)


class TestTaskCreate:
    """Test TaskCreate schema validation."""

    def test_valid_task_create(self):
        """Test creating TaskCreate with valid data."""
        task = TaskCreate(title="Buy groceries", description="Milk and eggs")
        assert task.title == "Buy groceries"
        assert task.description == "Milk and eggs"

    def test_task_create_default_description(self):
        """Test TaskCreate has empty string default for description."""
        task = TaskCreate(title="Call mom")
        assert task.title == "Call mom"
        assert task.description == ""

    def test_task_create_empty_title_fails(self):
        """Test TaskCreate fails with empty title."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="")

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)

    def test_task_create_title_too_long_fails(self):
        """Test TaskCreate fails with title > 200 characters."""
        long_title = "x" * 201
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)

    def test_task_create_description_max_length(self):
        """Test TaskCreate accepts description up to 500 characters."""
        description = "x" * 500
        task = TaskCreate(title="Test", description=description)
        assert len(task.description) == 500

    def test_task_create_description_too_long_fails(self):
        """Test TaskCreate fails with description > 500 characters."""
        long_description = "x" * 501
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", description=long_description)

        errors = exc_info.value.errors()
        assert any("description" in str(error["loc"]) for error in errors)


class TestTaskUpdate:
    """Test TaskUpdate schema validation."""

    def test_task_update_all_none(self):
        """Test TaskUpdate with all None values is valid."""
        task = TaskUpdate()
        assert task.title is None
        assert task.description is None

    def test_task_update_with_valid_title(self):
        """Test TaskUpdate with valid title."""
        task = TaskUpdate(title="Updated title")
        assert task.title == "Updated title"
        assert task.description is None

    def test_task_update_with_valid_description(self):
        """Test TaskUpdate with valid description."""
        task = TaskUpdate(description="Updated description")
        assert task.title is None
        assert task.description == "Updated description"

    def test_task_update_empty_title_fails(self):
        """Test TaskUpdate fails with empty title."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title="")

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)

    def test_task_update_title_too_long_fails(self):
        """Test TaskUpdate fails with title > 200 characters."""
        long_title = "x" * 201
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title=long_title)

        errors = exc_info.value.errors()
        assert any("title" in str(error["loc"]) for error in errors)


class TestTaskResponse:
    """Test TaskResponse schema."""

    def test_task_response_from_attributes(self):
        """Test TaskResponse can be created from SQLModel attributes."""
        # This tests the Config.from_attributes = True setting
        task_data = {
            "id": 1,
            "user_id": "user-123",
            "title": "Test Task",
            "description": "Test description",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        # Simulate creating from SQLModel instance
        task = TaskResponse(**task_data)
        assert task.id == 1
        assert task.user_id == "user-123"
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.completed is False


class TestMessageResponse:
    """Test MessageResponse schema."""

    def test_message_response_creation(self):
        """Test creating MessageResponse."""
        response = MessageResponse(message="Task deleted successfully")
        assert response.message == "Task deleted successfully"


class TestErrorResponse:
    """Test ErrorResponse schema."""

    def test_error_response_creation(self):
        """Test creating ErrorResponse."""
        error = ErrorResponse(detail="Task not found")
        assert error.detail == "Task not found"
