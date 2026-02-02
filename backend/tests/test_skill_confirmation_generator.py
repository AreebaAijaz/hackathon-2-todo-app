"""Test ConfirmationGeneratorSkill for generating user-friendly messages."""

import pytest

from skills.confirmation_generator import ConfirmationGeneratorSkill, TaskInfo


class TestConfirmationGeneratorSkill:
    """Test ConfirmationGeneratorSkill execution and message generation."""

    @pytest.fixture
    def skill(self):
        """Create a ConfirmationGeneratorSkill instance."""
        return ConfirmationGeneratorSkill()

    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return TaskInfo(id=1, title="Buy groceries", description="Milk and eggs")

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks for testing."""
        return [
            TaskInfo(id=1, title="Buy groceries", completed=False),
            TaskInfo(id=2, title="Call dentist", completed=True),
            TaskInfo(id=3, title="Walk dog", completed=False),
        ]

    def test_created_with_task(self, skill, sample_task):
        """Test 'created' action with task contains title."""
        result = skill.execute("created", task=sample_task)
        assert "Buy groceries" in result
        assert "added" in result.lower()

    def test_created_with_description(self, skill, sample_task):
        """Test 'created' action includes description if present."""
        result = skill.execute("created", task=sample_task)
        assert "Milk and eggs" in result

    def test_created_without_task(self, skill):
        """Test 'created' action without task returns generic message."""
        result = skill.execute("created")
        assert "created" in result.lower()
        assert "successfully" in result.lower()

    def test_completed_with_task(self, skill, sample_task):
        """Test 'completed' action with task contains title."""
        result = skill.execute("completed", task=sample_task)
        assert "Buy groceries" in result
        assert "complete" in result.lower()

    def test_completed_without_task(self, skill):
        """Test 'completed' action without task returns generic message."""
        result = skill.execute("completed")
        assert "complete" in result.lower()

    def test_deleted_with_task(self, skill, sample_task):
        """Test 'deleted' action with task contains title."""
        result = skill.execute("deleted", task=sample_task)
        assert "Buy groceries" in result
        assert "removed" in result.lower()

    def test_deleted_without_task(self, skill):
        """Test 'deleted' action without task returns generic message."""
        result = skill.execute("deleted")
        assert "deleted" in result.lower()

    def test_updated_with_changes(self, skill, sample_task):
        """Test 'updated' with changes lists the changes."""
        result = skill.execute("updated", task=sample_task, changes=["title"])
        assert "Buy groceries" in result
        assert "title" in result
        assert "updated" in result.lower()

    def test_updated_without_changes(self, skill, sample_task):
        """Test 'updated' without changes returns 'No changes'."""
        result = skill.execute("updated", task=sample_task, changes=None)
        assert "No changes" in result

    def test_updated_with_empty_changes(self, skill, sample_task):
        """Test 'updated' with empty changes list returns 'No changes'."""
        result = skill.execute("updated", task=sample_task, changes=[])
        assert "No changes" in result

    def test_listed_empty_tasks_pending_filter(self, skill):
        """Test 'listed' with empty tasks and filter='pending'."""
        result = skill.execute("listed", tasks=[], filter_applied="pending")
        assert "no pending tasks" in result.lower()

    def test_listed_empty_tasks_completed_filter(self, skill):
        """Test 'listed' with empty tasks and filter='completed'."""
        result = skill.execute("listed", tasks=[], filter_applied="completed")
        assert "haven't completed" in result.lower() or "completed any" in result.lower()

    def test_listed_empty_tasks_all_filter(self, skill):
        """Test 'listed' with empty tasks and filter='all'."""
        result = skill.execute("listed", tasks=[], filter_applied="all")
        assert "don't have any tasks" in result.lower()

    def test_listed_with_tasks_all_filter(self, skill, sample_tasks):
        """Test 'listed' with tasks, filter='all' shows count."""
        result = skill.execute("listed", tasks=sample_tasks, filter_applied="all")
        assert "3" in result or "three" in result.lower()
        assert "2 pending" in result
        assert "1 completed" in result

    def test_listed_with_one_pending_task(self, skill):
        """Test 'listed' with 1 pending task shows single task."""
        tasks = [TaskInfo(id=1, title="Buy groceries", completed=False)]
        result = skill.execute("listed", tasks=tasks, filter_applied="pending")
        assert "1 pending task" in result
        assert "Buy groceries" in result

    def test_listed_with_one_completed_task(self, skill):
        """Test 'listed' with 1 completed task shows single task."""
        tasks = [TaskInfo(id=1, title="Buy groceries", completed=True)]
        result = skill.execute("listed", tasks=tasks, filter_applied="completed")
        assert "1 task" in result
        assert "Buy groceries" in result

    def test_format_changes_single_item(self, skill):
        """Test _format_changes with 1 item."""
        result = skill._format_changes(["title"])
        assert result == "title"

    def test_format_changes_two_items(self, skill):
        """Test _format_changes with 2 items."""
        result = skill._format_changes(["title", "description"])
        assert "title and description" in result

    def test_format_changes_three_items(self, skill):
        """Test _format_changes with 3 items."""
        result = skill._format_changes(["title", "description", "status"])
        assert "title, description, and status" in result

    def test_already_completed_with_task(self, skill, sample_task):
        """Test 'already_completed' action with task."""
        result = skill.execute("already_completed", task=sample_task)
        assert "Buy groceries" in result
        assert "already" in result.lower()
        assert "complete" in result.lower()

    def test_already_completed_without_task(self, skill):
        """Test 'already_completed' action without task."""
        result = skill.execute("already_completed")
        assert "already completed" in result.lower()

    def test_unknown_action_returns_generic(self, skill):
        """Test unknown action returns generic message."""
        result = skill.execute("unknown_action")
        assert "Operation completed" in result
