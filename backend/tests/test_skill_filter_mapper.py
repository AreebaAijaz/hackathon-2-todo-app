"""Test FilterMapperSkill for mapping natural language to filter parameters."""

import pytest

from skills.filter_mapper import FilterMapperSkill, FilterParams


class TestFilterMapperSkill:
    """Test FilterMapperSkill execution and mapping logic."""

    @pytest.fixture
    def skill(self):
        """Create a FilterMapperSkill instance."""
        return FilterMapperSkill()

    def test_empty_input_returns_all(self, skill):
        """Test empty input defaults to status='all'."""
        result = skill.execute("")
        assert result.status == "all"

    def test_show_my_tasks(self, skill):
        """Test 'show my tasks' returns status='all'."""
        result = skill.execute("show my tasks")
        assert result.status == "all"

    def test_show_all_tasks_high_confidence(self, skill):
        """Test 'show all tasks' returns status='all' with high confidence."""
        result = skill.execute("show all tasks")
        assert result.status == "all"
        assert result.confidence >= 0.9

    def test_show_completed_tasks(self, skill):
        """Test 'show completed tasks' returns status='completed'."""
        result = skill.execute("show completed tasks")
        assert result.status == "completed"

    def test_what_have_i_finished(self, skill):
        """Test 'what have I finished' returns status='completed'."""
        result = skill.execute("what have I finished")
        assert result.status == "completed"

    def test_what_have_i_done(self, skill):
        """Test 'what have I done' returns status='completed'."""
        result = skill.execute("what have I done")
        assert result.status == "completed"

    def test_show_pending_tasks(self, skill):
        """Test 'show pending tasks' returns status='pending'."""
        result = skill.execute("show pending tasks")
        assert result.status == "pending"

    def test_whats_left_to_do(self, skill):
        """Test 'what's left to do' returns status='pending'."""
        result = skill.execute("what's left to do")
        assert result.status == "pending"

    def test_what_do_i_still_need_to_do(self, skill):
        """Test 'what do I still need to do' returns status='pending'."""
        result = skill.execute("what do I still need to do")
        assert result.status == "pending"

    def test_show_everything(self, skill):
        """Test 'show everything' returns status='all'."""
        result = skill.execute("show everything")
        assert result.status == "all"

    def test_incomplete_tasks(self, skill):
        """Test 'incomplete tasks' returns status='pending'."""
        result = skill.execute("show incomplete tasks")
        assert result.status == "pending"

    def test_finished_tasks(self, skill):
        """Test 'finished tasks' returns status='completed'."""
        result = skill.execute("list finished tasks")
        assert result.status == "completed"

    def test_outstanding_tasks(self, skill):
        """Test 'outstanding tasks' returns status='pending'."""
        result = skill.execute("what are my outstanding tasks")
        assert result.status == "pending"

    def test_open_tasks(self, skill):
        """Test 'open tasks' returns status='pending'."""
        result = skill.execute("show me open tasks")
        assert result.status == "pending"

    def test_active_tasks(self, skill):
        """Test 'active tasks' returns status='pending'."""
        result = skill.execute("my active tasks")
        assert result.status == "pending"

    def test_full_list(self, skill):
        """Test 'full list' returns status='all'."""
        result = skill.execute("give me the full list")
        assert result.status == "all"

    def test_accomplished_tasks(self, skill):
        """Test 'accomplished' returns status='completed'."""
        result = skill.execute("what have I accomplished")
        assert result.status == "completed"

    def test_checked_off_tasks(self, skill):
        """Test 'checked off' returns status='completed'."""
        result = skill.execute("show checked off tasks")
        assert result.status == "completed"

    def test_generic_query_defaults_to_all(self, skill):
        """Test generic query defaults to status='all' with lower confidence."""
        result = skill.execute("show me stuff")
        assert result.status == "all"
        assert result.confidence < 0.9
