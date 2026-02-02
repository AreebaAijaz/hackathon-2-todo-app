"""Test ContextBuilderSkill for building conversation context."""

import pytest

from skills.context_builder import ContextBuilderSkill, MessageContext, BuiltContext


class TestContextBuilderSkill:
    """Test ContextBuilderSkill execution and context building."""

    @pytest.fixture
    def skill(self):
        """Create a ContextBuilderSkill instance."""
        return ContextBuilderSkill()

    def test_empty_history_with_system_prompt(self, skill):
        """Test empty history with system prompt returns 2 messages."""
        result = skill.execute(
            conversation_history=[],
            user_message="Hello",
            include_system_prompt=True
        )

        assert len(result.messages) == 2
        assert result.messages[0]["role"] == "system"
        assert result.messages[1]["role"] == "user"
        assert result.messages[1]["content"] == "Hello"

    def test_empty_history_without_system_prompt(self, skill):
        """Test empty history without system prompt returns 1 message."""
        result = skill.execute(
            conversation_history=[],
            user_message="Hello",
            include_system_prompt=False
        )

        assert len(result.messages) == 1
        assert result.messages[0]["role"] == "user"
        assert result.messages[0]["content"] == "Hello"

    def test_history_with_messages(self, skill):
        """Test history with messages includes all messages."""
        history = [
            MessageContext(role="user", content="List my tasks"),
            MessageContext(role="assistant", content="You have 3 tasks"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Show completed ones",
            include_system_prompt=True
        )

        # System + 2 history + 1 new user message = 4
        assert len(result.messages) == 4
        assert result.messages[0]["role"] == "system"
        assert result.messages[1]["role"] == "user"
        assert result.messages[1]["content"] == "List my tasks"
        assert result.messages[2]["role"] == "assistant"
        assert result.messages[2]["content"] == "You have 3 tasks"
        assert result.messages[3]["role"] == "user"
        assert result.messages[3]["content"] == "Show completed ones"

    def test_history_exceeding_max_messages_truncated(self, skill):
        """Test history exceeding MAX_HISTORY_MESSAGES is truncated."""
        # Create 25 messages (more than MAX_HISTORY_MESSAGES = 20)
        history = [
            MessageContext(role="user", content=f"Message {i}")
            for i in range(25)
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Latest message",
            include_system_prompt=True
        )

        # System + 20 most recent history + 1 new user message = 22
        assert len(result.messages) == 22
        assert result.messages[0]["role"] == "system"
        # Should have the last 20 messages from history
        assert result.messages[1]["content"] == "Message 5"  # (25 - 20 = 5)
        assert result.messages[20]["content"] == "Message 24"
        assert result.messages[21]["content"] == "Latest message"

    def test_build_minimal_context(self, skill):
        """Test build_minimal_context creates context with system prompt."""
        result = skill.build_minimal_context("Hello")

        assert len(result.messages) == 2
        assert result.messages[0]["role"] == "system"
        assert result.messages[1]["role"] == "user"
        assert result.messages[1]["content"] == "Hello"

    def test_extract_recent_task_ids(self, skill):
        """Test _extract_recent_task_ids finds IDs from assistant messages."""
        history = [
            MessageContext(role="user", content="Show my tasks"),
            MessageContext(role="assistant", content="Here are your tasks: task 5, task 12"),
            MessageContext(role="user", content="Complete task 5"),
            MessageContext(role="assistant", content="Task ID: 5 completed"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="What's next?",
            include_system_prompt=False
        )

        assert 5 in result.recent_task_ids
        assert 12 in result.recent_task_ids

    def test_extract_recent_task_ids_with_hash(self, skill):
        """Test _extract_recent_task_ids finds IDs with task keyword."""
        history = [
            MessageContext(role="assistant", content="Completed task #3 and task 7"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Show all",
            include_system_prompt=False
        )

        # The regex looks for "task" or "id" followed by the number
        assert 3 in result.recent_task_ids
        assert 7 in result.recent_task_ids

    def test_extract_last_action_added(self, skill):
        """Test _extract_last_action finds 'add' action."""
        history = [
            MessageContext(role="assistant", content="I've added 'Buy milk' to your tasks"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Thanks",
            include_system_prompt=False
        )

        assert result.last_action == "add"

    def test_extract_last_action_completed(self, skill):
        """Test _extract_last_action finds 'complete' action."""
        history = [
            MessageContext(role="assistant", content="Task completed successfully"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Great",
            include_system_prompt=False
        )

        assert result.last_action == "complete"

    def test_extract_last_action_deleted(self, skill):
        """Test _extract_last_action finds 'delete' action."""
        history = [
            MessageContext(role="assistant", content="I've removed that task"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="OK",
            include_system_prompt=False
        )

        assert result.last_action == "delete"

    def test_extract_last_action_listed(self, skill):
        """Test _extract_last_action finds 'list' action."""
        history = [
            MessageContext(role="assistant", content="I'm showing your tasks now"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Show completed",
            include_system_prompt=False
        )

        assert result.last_action == "list"

    def test_extract_last_action_no_action(self, skill):
        """Test _extract_last_action returns None when no action found."""
        history = [
            MessageContext(role="assistant", content="Hello, how can I help?"),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="List tasks",
            include_system_prompt=False
        )

        assert result.last_action is None

    def test_system_prompt_content(self, skill):
        """Test system prompt contains expected guidance."""
        result = skill.execute(
            conversation_history=[],
            user_message="Hello",
            include_system_prompt=True
        )

        system_content = result.messages[0]["content"]
        assert "task management assistant" in system_content.lower()
        assert "adding new tasks" in system_content.lower()
        assert "listing" in system_content.lower()

    def test_recent_task_ids_limited_to_five(self, skill):
        """Test recent_task_ids returns at most 5 IDs."""
        history = [
            MessageContext(
                role="assistant",
                content="Tasks: task 1, task 2, task 3, task 4, task 5, task 6, task 7"
            ),
        ]

        result = skill.execute(
            conversation_history=history,
            user_message="Show all",
            include_system_prompt=False
        )

        assert len(result.recent_task_ids) <= 5

    def test_built_context_has_default_empty_recent_task_ids(self, skill):
        """Test BuiltContext initializes recent_task_ids as empty list."""
        context = BuiltContext(messages=[])
        assert context.recent_task_ids == []
