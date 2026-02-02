"""Test IDResolverSkill for resolving task references to IDs."""

import pytest

from skills.id_resolver import IDResolverSkill, TaskReference, ResolvedTask


class TestIDResolverSkill:
    """Test IDResolverSkill execution and resolution logic."""

    @pytest.fixture
    def skill(self):
        """Create an IDResolverSkill instance."""
        return IDResolverSkill()

    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks for testing."""
        return [
            TaskReference(id=5, title="Buy groceries", completed=False),
            TaskReference(id=3, title="Call dentist", completed=True),
            TaskReference(id=7, title="Walk the dog", completed=False),
            TaskReference(id=1, title="Finish report", completed=False),
        ]

    def test_empty_input_returns_none(self, skill, sample_tasks):
        """Test empty input returns task_id=None."""
        result = skill.execute("", sample_tasks)
        assert result.task_id is None

    def test_empty_tasks_list_returns_none(self, skill):
        """Test empty tasks list returns task_id=None."""
        result = skill.execute("task 5", [])
        assert result.task_id is None

    def test_task_5_resolves(self, skill, sample_tasks):
        """Test 'task 5' resolves to task with id=5."""
        result = skill.execute("task 5", sample_tasks)
        assert result.task_id == 5
        assert result.resolution_method == "exact_id"
        assert result.confidence == 1.0

    def test_task_hash_5_resolves(self, skill, sample_tasks):
        """Test 'task #5' resolves to task with id=5."""
        result = skill.execute("task #5", sample_tasks)
        assert result.task_id == 5
        assert result.resolution_method == "exact_id"

    def test_hash_3_resolves(self, skill, sample_tasks):
        """Test '#3' resolves to task with id=3."""
        result = skill.execute("#3", sample_tasks)
        assert result.task_id == 3
        assert result.resolution_method == "exact_id"

    def test_first_task_resolves(self, skill, sample_tasks):
        """Test 'first task' resolves to first task in list."""
        result = skill.execute("first task", sample_tasks)
        assert result.task_id == 5  # First in sample_tasks
        assert result.resolution_method == "ordinal"

    def test_last_task_resolves_to_first(self, skill, sample_tasks):
        """Test 'last task' resolves to first task (newest-first sorting)."""
        result = skill.execute("last task", sample_tasks)
        assert result.task_id == 5  # First in sample_tasks (newest)
        assert result.resolution_method == "ordinal"

    def test_second_task_resolves(self, skill, sample_tasks):
        """Test 'second task' resolves to second task in list."""
        result = skill.execute("second task", sample_tasks)
        assert result.task_id == 3  # Second in sample_tasks
        assert result.resolution_method == "ordinal"

    def test_title_match_groceries(self, skill, sample_tasks):
        """Test 'groceries' matches task titled 'Buy groceries'."""
        result = skill.execute("groceries", sample_tasks)
        assert result.task_id == 5
        assert result.resolution_method == "title_match"
        assert result.matched_title == "Buy groceries"

    def test_title_match_dentist(self, skill, sample_tasks):
        """Test 'dentist' matches task titled 'Call dentist'."""
        result = skill.execute("the dentist task", sample_tasks)
        assert result.task_id == 3
        assert result.resolution_method == "title_match"

    def test_title_match_dog(self, skill, sample_tasks):
        """Test 'dog' matches task titled 'Walk the dog'."""
        result = skill.execute("walk dog", sample_tasks)
        assert result.task_id == 7
        assert result.resolution_method == "title_match"

    def test_no_match_returns_none(self, skill, sample_tasks):
        """Test no match returns task_id=None."""
        result = skill.execute("nonexistent task", sample_tasks)
        assert result.task_id is None

    def test_id_not_in_list_returns_none(self, skill, sample_tasks):
        """Test ID that doesn't exist in list returns None."""
        result = skill.execute("task 999", sample_tasks)
        assert result.task_id is None

    def test_latest_task_resolves(self, skill, sample_tasks):
        """Test 'latest task' resolves to first task."""
        result = skill.execute("latest task", sample_tasks)
        assert result.task_id == 5
        assert result.resolution_method == "ordinal"

    def test_newest_task_resolves(self, skill, sample_tasks):
        """Test 'newest task' resolves to first task."""
        result = skill.execute("newest task", sample_tasks)
        assert result.task_id == 5
        assert result.resolution_method == "ordinal"

    def test_id_pattern_with_number(self, skill, sample_tasks):
        """Test 'id 3' pattern resolves."""
        result = skill.execute("id 3", sample_tasks)
        assert result.task_id == 3
        assert result.resolution_method == "exact_id"

    def test_id_pattern_with_colon(self, skill, sample_tasks):
        """Test 'id: 7' pattern resolves."""
        result = skill.execute("id: 7", sample_tasks)
        assert result.task_id == 7
        assert result.resolution_method == "exact_id"

    def test_title_match_confidence_score(self, skill, sample_tasks):
        """Test title match returns confidence score."""
        result = skill.execute("buy groceries", sample_tasks)
        assert result.task_id == 5
        assert result.confidence > 0.5
