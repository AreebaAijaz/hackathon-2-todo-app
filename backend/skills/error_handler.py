"""Error Handler Skill - Handle errors gracefully with user-friendly messages."""

from typing import Optional, Type
from dataclasses import dataclass

from .base import BaseSkill


@dataclass
class ErrorResponse:
    """Structured error response."""
    message: str
    error_type: str
    suggestion: Optional[str] = None
    recoverable: bool = True


class ErrorHandlerSkill(BaseSkill):
    """Convert exceptions and error states into user-friendly messages.

    Handles:
    - Task not found errors
    - Authorization errors
    - Validation errors
    - Database errors
    - General exceptions
    """

    name = "error_handler"
    description = "Handles errors gracefully with user-friendly messages"

    # Error type mappings
    ERROR_MESSAGES = {
        "TaskNotFoundError": {
            "message": "I couldn't find that task.",
            "suggestion": "Would you like me to show you your current tasks?",
            "recoverable": True,
        },
        "UnauthorizedError": {
            "message": "You don't have permission to access that task.",
            "suggestion": "Please make sure you're referring to one of your own tasks.",
            "recoverable": True,
        },
        "ValidationError": {
            "message": "There was a problem with the task details.",
            "suggestion": "Please check that the title is between 1-200 characters.",
            "recoverable": True,
        },
        "DatabaseError": {
            "message": "I'm having trouble accessing the database right now.",
            "suggestion": "Please try again in a moment.",
            "recoverable": True,
        },
        "ValueError": {
            "message": "I didn't quite understand that.",
            "suggestion": "Could you try rephrasing your request?",
            "recoverable": True,
        },
    }

    def execute(
        self,
        error: Optional[Exception] = None,
        error_type: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs
    ) -> ErrorResponse:
        """Convert an error into a user-friendly response.

        Args:
            error: The exception that occurred (optional)
            error_type: String error type if no exception (optional)
            context: Additional context about what was being attempted

        Returns:
            ErrorResponse with user-friendly message and suggestions
        """
        # Determine error type
        if error:
            error_type = type(error).__name__

        if not error_type:
            error_type = "UnknownError"

        # Get error info from mappings or use defaults
        error_info = self.ERROR_MESSAGES.get(error_type, {
            "message": "Something went wrong.",
            "suggestion": "Please try again or rephrase your request.",
            "recoverable": True,
        })

        # Build message
        message = error_info["message"]

        # Add context if provided
        if context:
            message = f"{context}: {message}"

        # Add specific error details for known types
        if error and error_type == "TaskNotFoundError":
            # Try to extract task ID from error message
            error_str = str(error)
            if "ID" in error_str:
                message = f"I couldn't find a task with that ID."

        return ErrorResponse(
            message=message,
            error_type=error_type,
            suggestion=error_info.get("suggestion"),
            recoverable=error_info.get("recoverable", True),
        )

    def format_response(self, error_response: ErrorResponse) -> str:
        """Format an ErrorResponse into a complete message string.

        Args:
            error_response: The structured error response

        Returns:
            Formatted string message
        """
        parts = [error_response.message]

        if error_response.suggestion:
            parts.append(error_response.suggestion)

        return " ".join(parts)


# Singleton instance
error_handler = ErrorHandlerSkill()
