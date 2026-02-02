"""Test ErrorHandlerSkill for handling errors gracefully."""

import pytest

from skills.error_handler import ErrorHandlerSkill, ErrorResponse


class TestErrorHandlerSkill:
    """Test ErrorHandlerSkill execution and error handling."""

    @pytest.fixture
    def skill(self):
        """Create an ErrorHandlerSkill instance."""
        return ErrorHandlerSkill()

    def test_value_error_exception(self, skill):
        """Test ValueError exception is mapped to user-friendly message."""
        error = ValueError("Invalid input")
        result = skill.execute(error=error)

        assert result.error_type == "ValueError"
        assert "didn't quite understand" in result.message
        assert result.suggestion is not None
        assert result.recoverable is True

    def test_unknown_exception_type(self, skill):
        """Test unknown exception type returns generic message."""
        error = RuntimeError("Something went wrong")
        result = skill.execute(error=error)

        assert result.error_type == "RuntimeError"
        assert "Something went wrong" in result.message
        assert result.recoverable is True

    def test_error_type_string_task_not_found(self, skill):
        """Test error_type string 'TaskNotFoundError' is mapped."""
        result = skill.execute(error_type="TaskNotFoundError")

        assert result.error_type == "TaskNotFoundError"
        assert "couldn't find that task" in result.message
        assert result.suggestion is not None

    def test_no_error_and_no_error_type(self, skill):
        """Test no error and no error_type defaults to 'UnknownError'."""
        result = skill.execute()

        assert result.error_type == "UnknownError"
        assert "Something went wrong" in result.message

    def test_with_context_string(self, skill):
        """Test error with context string prepends context to message."""
        result = skill.execute(
            error_type="TaskNotFoundError",
            context="While deleting task"
        )

        assert "While deleting task" in result.message
        assert "couldn't find that task" in result.message

    def test_format_response_with_suggestion(self, skill):
        """Test format_response includes both message and suggestion."""
        error_response = ErrorResponse(
            message="I couldn't find that task.",
            error_type="TaskNotFoundError",
            suggestion="Would you like me to show you your current tasks?",
        )

        formatted = skill.format_response(error_response)
        assert "couldn't find that task" in formatted
        assert "Would you like me to show you" in formatted

    def test_format_response_without_suggestion(self, skill):
        """Test format_response without suggestion returns just message."""
        error_response = ErrorResponse(
            message="Task deleted.",
            error_type="Success",
            suggestion=None,
        )

        formatted = skill.format_response(error_response)
        assert formatted == "Task deleted."

    def test_unauthorized_error_mapping(self, skill):
        """Test UnauthorizedError mapping."""
        result = skill.execute(error_type="UnauthorizedError")

        assert result.error_type == "UnauthorizedError"
        assert "don't have permission" in result.message
        assert "own tasks" in result.suggestion

    def test_validation_error_mapping(self, skill):
        """Test ValidationError mapping."""
        result = skill.execute(error_type="ValidationError")

        assert result.error_type == "ValidationError"
        assert "problem with the task details" in result.message
        assert "1-200 characters" in result.suggestion

    def test_database_error_mapping(self, skill):
        """Test DatabaseError mapping."""
        result = skill.execute(error_type="DatabaseError")

        assert result.error_type == "DatabaseError"
        assert "trouble accessing the database" in result.message
        assert "try again" in result.suggestion

    def test_all_errors_are_recoverable(self, skill):
        """Test all predefined errors are marked as recoverable."""
        error_types = [
            "TaskNotFoundError",
            "UnauthorizedError",
            "ValidationError",
            "DatabaseError",
            "ValueError",
        ]

        for error_type in error_types:
            result = skill.execute(error_type=error_type)
            assert result.recoverable is True

    def test_error_response_dataclass_fields(self, skill):
        """Test ErrorResponse has correct fields."""
        result = skill.execute(error_type="TaskNotFoundError")

        assert hasattr(result, "message")
        assert hasattr(result, "error_type")
        assert hasattr(result, "suggestion")
        assert hasattr(result, "recoverable")
        assert isinstance(result.message, str)
        assert isinstance(result.error_type, str)
