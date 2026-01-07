"""Tests for the TaskStorage class."""

import pytest

from src.storage import TaskStorage, TaskNotFoundError
from src.models import ValidationError


class TestTaskStorageAdd:
    """Tests for add_task method."""

    def test_add_task_with_title_only(self) -> None:
        """Test adding a task with just a title."""
        storage = TaskStorage()
        task = storage.add_task("Buy groceries")

        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert len(storage.get_all_tasks()) == 1

    def test_add_task_with_description(self) -> None:
        """Test adding a task with title and description."""
        storage = TaskStorage()
        task = storage.add_task("Meeting", "Team sync at 3pm")

        assert task.title == "Meeting"
        assert task.description == "Team sync at 3pm"

    def test_add_task_with_invalid_title(self) -> None:
        """Test that adding task with empty title raises error."""
        storage = TaskStorage()
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            storage.add_task("")

    def test_add_multiple_tasks(self) -> None:
        """Test adding multiple tasks."""
        storage = TaskStorage()
        storage.add_task("Task 1")
        storage.add_task("Task 2")
        storage.add_task("Task 3")

        assert len(storage.get_all_tasks()) == 3


class TestTaskStorageGet:
    """Tests for get methods."""

    def test_get_all_tasks_empty(self) -> None:
        """Test getting all tasks when storage is empty."""
        storage = TaskStorage()
        tasks = storage.get_all_tasks()

        assert tasks == []

    def test_get_all_tasks_returns_copy(self) -> None:
        """Test that get_all_tasks returns a copy, not the internal list."""
        storage = TaskStorage()
        storage.add_task("Task 1")

        tasks = storage.get_all_tasks()
        tasks.clear()

        assert len(storage.get_all_tasks()) == 1

    def test_get_task_by_id_found(self) -> None:
        """Test getting a task by its ID."""
        storage = TaskStorage()
        created_task = storage.add_task("Find me")

        found_task = storage.get_task_by_id(created_task.id)

        assert found_task is not None
        assert found_task.id == created_task.id
        assert found_task.title == "Find me"

    def test_get_task_by_id_not_found(self) -> None:
        """Test getting a task with non-existent ID."""
        storage = TaskStorage()
        result = storage.get_task_by_id("non-existent-id")

        assert result is None


class TestTaskStorageUpdate:
    """Tests for update_task method."""

    def test_update_title(self) -> None:
        """Test updating just the title."""
        storage = TaskStorage()
        task = storage.add_task("Original", "Description")

        updated = storage.update_task(task.id, title="Updated")

        assert updated.title == "Updated"
        assert updated.description == "Description"

    def test_update_description(self) -> None:
        """Test updating just the description."""
        storage = TaskStorage()
        task = storage.add_task("Title", "Original desc")

        updated = storage.update_task(task.id, description="New desc")

        assert updated.title == "Title"
        assert updated.description == "New desc"

    def test_update_both_fields(self) -> None:
        """Test updating both title and description."""
        storage = TaskStorage()
        task = storage.add_task("Old title", "Old desc")

        updated = storage.update_task(task.id, title="New title", description="New desc")

        assert updated.title == "New title"
        assert updated.description == "New desc"

    def test_update_with_no_changes(self) -> None:
        """Test update with no new values keeps original."""
        storage = TaskStorage()
        task = storage.add_task("Title", "Description")

        updated = storage.update_task(task.id)

        assert updated.title == "Title"
        assert updated.description == "Description"

    def test_update_nonexistent_task(self) -> None:
        """Test updating a task that doesn't exist."""
        storage = TaskStorage()
        with pytest.raises(TaskNotFoundError) as exc_info:
            storage.update_task("fake-id", title="New")

        assert "fake-id" in str(exc_info.value)

    def test_update_with_invalid_title(self) -> None:
        """Test updating with invalid title raises error."""
        storage = TaskStorage()
        task = storage.add_task("Valid")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            storage.update_task(task.id, title="")


class TestTaskStorageDelete:
    """Tests for delete_task method."""

    def test_delete_task(self) -> None:
        """Test deleting an existing task."""
        storage = TaskStorage()
        task = storage.add_task("Delete me")

        result = storage.delete_task(task.id)

        assert result is True
        assert len(storage.get_all_tasks()) == 0

    def test_delete_nonexistent_task(self) -> None:
        """Test deleting a task that doesn't exist."""
        storage = TaskStorage()
        with pytest.raises(TaskNotFoundError) as exc_info:
            storage.delete_task("fake-id")

        assert "fake-id" in str(exc_info.value)

    def test_delete_one_of_many(self) -> None:
        """Test deleting one task from multiple."""
        storage = TaskStorage()
        task1 = storage.add_task("Keep me")
        task2 = storage.add_task("Delete me")
        task3 = storage.add_task("Keep me too")

        storage.delete_task(task2.id)

        tasks = storage.get_all_tasks()
        assert len(tasks) == 2
        assert all(t.id != task2.id for t in tasks)


class TestTaskStorageToggle:
    """Tests for toggle_complete method."""

    def test_toggle_incomplete_to_complete(self) -> None:
        """Test toggling incomplete task to complete."""
        storage = TaskStorage()
        task = storage.add_task("Toggle me")
        assert task.completed is False

        toggled = storage.toggle_complete(task.id)

        assert toggled.completed is True

    def test_toggle_complete_to_incomplete(self) -> None:
        """Test toggling complete task to incomplete."""
        storage = TaskStorage()
        task = storage.add_task("Toggle me")
        storage.toggle_complete(task.id)  # Now complete

        toggled = storage.toggle_complete(task.id)

        assert toggled.completed is False

    def test_toggle_nonexistent_task(self) -> None:
        """Test toggling a task that doesn't exist."""
        storage = TaskStorage()
        with pytest.raises(TaskNotFoundError) as exc_info:
            storage.toggle_complete("fake-id")

        assert "fake-id" in str(exc_info.value)

    def test_multiple_toggles(self) -> None:
        """Test multiple toggle operations."""
        storage = TaskStorage()
        task = storage.add_task("Toggle many times")

        storage.toggle_complete(task.id)  # True
        storage.toggle_complete(task.id)  # False
        storage.toggle_complete(task.id)  # True

        assert task.completed is True
