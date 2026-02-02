"""Test SQLModel models and their methods."""

import json
from datetime import datetime

from models import Task, Conversation, Message


class TestMessageModel:
    """Test Message model helper methods."""

    def test_get_tool_calls_list_with_none(self):
        """Test get_tool_calls_list returns empty list when tool_calls is None."""
        message = Message(
            conversation_id=1,
            user_id="user-123",
            role="user",
            content="Hello",
            tool_calls=None,
        )
        assert message.get_tool_calls_list() == []

    def test_get_tool_calls_list_with_json(self):
        """Test get_tool_calls_list parses JSON string to list."""
        tool_calls = [
            {"name": "list_tasks", "args": {}},
            {"name": "create_task", "args": {"title": "Test"}},
        ]
        message = Message(
            conversation_id=1,
            user_id="user-123",
            role="assistant",
            content="Here are your tasks",
            tool_calls=json.dumps(tool_calls),
        )
        assert message.get_tool_calls_list() == tool_calls

    def test_set_tool_calls_list_with_list(self):
        """Test set_tool_calls_list converts list to JSON string."""
        message = Message(
            conversation_id=1,
            user_id="user-123",
            role="assistant",
            content="Done",
        )
        tool_calls = [{"name": "create_task", "args": {"title": "Buy milk"}}]
        message.set_tool_calls_list(tool_calls)

        assert message.tool_calls is not None
        assert json.loads(message.tool_calls) == tool_calls

    def test_set_tool_calls_list_with_empty_list(self):
        """Test set_tool_calls_list sets None for empty list."""
        message = Message(
            conversation_id=1,
            user_id="user-123",
            role="assistant",
            content="Done",
            tool_calls=json.dumps([{"name": "test"}]),
        )
        message.set_tool_calls_list([])
        assert message.tool_calls is None

    def test_set_tool_calls_list_with_none(self):
        """Test set_tool_calls_list sets None when passed None."""
        message = Message(
            conversation_id=1,
            user_id="user-123",
            role="assistant",
            content="Done",
            tool_calls=json.dumps([{"name": "test"}]),
        )
        message.set_tool_calls_list(None)
        assert message.tool_calls is None


class TestTaskModel:
    """Test Task model default values."""

    def test_task_default_values(self):
        """Test Task model has correct default values."""
        task = Task(user_id="user-123", title="Test Task")

        assert task.completed is False
        assert task.description == ""
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_with_description(self):
        """Test Task model with explicit description."""
        task = Task(
            user_id="user-123",
            title="Test Task",
            description="Test description",
        )
        assert task.description == "Test description"

    def test_task_with_completed(self):
        """Test Task model with explicit completed status."""
        task = Task(
            user_id="user-123",
            title="Test Task",
            completed=True,
        )
        assert task.completed is True


class TestConversationModel:
    """Test Conversation model default values."""

    def test_conversation_default_values(self):
        """Test Conversation model has correct default values."""
        conversation = Conversation(user_id="user-123")

        assert conversation.title is None
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_conversation_with_title(self):
        """Test Conversation model with explicit title."""
        conversation = Conversation(
            user_id="user-123",
            title="My Tasks Discussion",
        )
        assert conversation.title == "My Tasks Discussion"
