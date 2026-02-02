"""Test TaskParserSkill for extracting task details from natural language."""

import pytest

from skills.task_parser import TaskParserSkill, ParsedTask


class TestTaskParserSkill:
    """Test TaskParserSkill execution and parsing logic."""

    @pytest.fixture
    def skill(self):
        """Create a TaskParserSkill instance."""
        return TaskParserSkill()

    def test_empty_input_returns_no_title(self, skill):
        """Test empty input returns has_title=False."""
        result = skill.execute("")
        assert result.has_title is False
        assert result.title == ""

    def test_whitespace_only_returns_no_title(self, skill):
        """Test whitespace-only input returns has_title=False."""
        result = skill.execute("   \n\t   ")
        assert result.has_title is False

    def test_simple_task_add(self, skill):
        """Test 'add task buy groceries' extracts title."""
        result = skill.execute("add task buy groceries")
        assert result.has_title is True
        assert result.title == "Buy groceries"
        assert result.description is None

    def test_create_new_task(self, skill):
        """Test 'create a new task meeting with john' extracts title."""
        result = skill.execute("create a new task meeting with john")
        assert result.has_title is True
        assert result.title == "Meeting with john"
        assert result.description is None

    def test_remind_me_to(self, skill):
        """Test 'remind me to call mom' extracts title."""
        result = skill.execute("remind me to call mom")
        assert result.has_title is True
        assert result.title == "Call mom"
        assert result.description is None

    def test_task_with_description_keyword(self, skill):
        """Test 'buy milk with description get 2% milk' extracts both."""
        result = skill.execute("buy milk with description get 2% milk")
        assert result.has_title is True
        assert result.title == "Buy milk"
        assert result.description == "get 2% milk"

    def test_task_with_dash_separator(self, skill):
        """Test 'buy milk - get 2% milk' extracts both."""
        result = skill.execute("buy milk - get 2% milk")
        assert result.has_title is True
        assert result.title == "Buy milk"
        assert result.description == "get 2% milk"

    def test_task_with_parentheses(self, skill):
        """Test 'buy milk (get 2% milk)' extracts both."""
        result = skill.execute("buy milk (get 2% milk)")
        assert result.has_title is True
        assert result.title == "Buy milk"
        assert result.description == "get 2% milk"

    def test_quoted_title(self, skill):
        """Test quoted title '"walk the dog"' is cleaned."""
        result = skill.execute('add task "walk the dog"')
        assert result.has_title is True
        assert result.title == "Walk the dog"

    def test_single_quoted_title(self, skill):
        """Test single-quoted title is cleaned."""
        result = skill.execute("add task 'call dentist'")
        assert result.has_title is True
        assert result.title == "Call dentist"

    def test_capitalize_first_letter(self, skill):
        """Test title is capitalized."""
        result = skill.execute("add task buy groceries")
        assert result.title[0].isupper()

    def test_please_prefix(self, skill):
        """Test 'please' prefix is removed."""
        result = skill.execute("please create a task to buy milk")
        assert result.has_title is True
        assert "please" not in result.title.lower()

    def test_i_want_to_prefix(self, skill):
        """Test 'I want to' prefix is removed."""
        result = skill.execute("I want to add a task buy groceries")
        assert result.has_title is True
        assert result.title == "Buy groceries"

    def test_multiple_prefixes_removed(self, skill):
        """Test multiple prefixes are handled."""
        result = skill.execute("please could you create a new task called meeting")
        assert result.has_title is True
        assert result.title == "Meeting"

    def test_task_with_colon_separator(self, skill):
        """Test 'task: buy milk' format."""
        result = skill.execute("task: buy milk")
        assert result.has_title is True
        assert result.title == "Buy milk"

    def test_description_with_details_keyword(self, skill):
        """Test 'with details' keyword for description."""
        result = skill.execute("buy milk with details get 2% organic")
        assert result.has_title is True
        assert result.title == "Buy milk"
        assert result.description == "get 2% organic"
