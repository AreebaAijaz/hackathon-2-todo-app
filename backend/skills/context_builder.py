"""Context Builder Skill - Build context from conversation history."""

from typing import List, Optional
from dataclasses import dataclass

from .base import BaseSkill


@dataclass
class MessageContext:
    """A message in the conversation context."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class BuiltContext:
    """Built context ready for AI agent."""
    messages: List[dict]  # OpenAI message format
    summary: Optional[str] = None
    recent_task_ids: List[int] = None
    last_action: Optional[str] = None

    def __post_init__(self):
        if self.recent_task_ids is None:
            self.recent_task_ids = []


class ContextBuilderSkill(BaseSkill):
    """Build conversation context for AI agents.

    Responsibilities:
    - Format conversation history for OpenAI API
    - Extract relevant context (recent task IDs, last actions)
    - Build system prompts with user context
    - Truncate history if needed while preserving important context
    """

    name = "context_builder"
    description = "Builds conversation context for AI agents"

    MAX_HISTORY_MESSAGES = 20  # Maximum messages to include

    SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their tasks by:
- Adding new tasks
- Listing their tasks (all, pending, or completed)
- Marking tasks as complete
- Updating task details
- Deleting tasks

Be conversational and friendly. When users refer to tasks by name or description,
try to match them to existing tasks. Confirm actions after completing them.

Important guidelines:
- Keep responses concise and helpful
- Confirm task operations with clear feedback
- If unsure which task the user means, ask for clarification
- Proactively offer relevant actions (e.g., after listing tasks, offer to help with pending ones)
"""

    def execute(
        self,
        conversation_history: List[MessageContext],
        user_message: str,
        include_system_prompt: bool = True,
        **kwargs
    ) -> BuiltContext:
        """Build context from conversation history.

        Args:
            conversation_history: Previous messages in the conversation
            user_message: The current user message to add
            include_system_prompt: Whether to include the system prompt

        Returns:
            BuiltContext with formatted messages for OpenAI API
        """
        messages = []

        # Add system prompt if requested
        if include_system_prompt:
            messages.append({
                "role": "system",
                "content": self.SYSTEM_PROMPT
            })

        # Add conversation history (truncated if needed)
        history_to_include = self._truncate_history(conversation_history)

        for msg in history_to_include:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Extract context from history
        recent_task_ids = self._extract_recent_task_ids(conversation_history)
        last_action = self._extract_last_action(conversation_history)

        return BuiltContext(
            messages=messages,
            recent_task_ids=recent_task_ids,
            last_action=last_action
        )

    def _truncate_history(self, history: List[MessageContext]) -> List[MessageContext]:
        """Truncate history to fit within limits while preserving recent context."""
        if len(history) <= self.MAX_HISTORY_MESSAGES:
            return history

        # Keep the most recent messages
        return history[-self.MAX_HISTORY_MESSAGES:]

    def _extract_recent_task_ids(self, history: List[MessageContext]) -> List[int]:
        """Extract task IDs mentioned in recent conversation."""
        import re

        task_ids = []
        # Look at recent assistant messages for task IDs
        for msg in reversed(history[-10:]):
            if msg.role == "assistant":
                # Look for patterns like "task 5", "ID: 5", "#5"
                matches = re.findall(r'(?:task|id)[:\s#]*(\d+)', msg.content, re.IGNORECASE)
                for match in matches:
                    task_id = int(match)
                    if task_id not in task_ids:
                        task_ids.append(task_id)

        return task_ids[:5]  # Return at most 5 recent IDs

    def _extract_last_action(self, history: List[MessageContext]) -> Optional[str]:
        """Extract the last action performed from conversation history."""
        action_keywords = {
            "added": "add",
            "created": "add",
            "completed": "complete",
            "finished": "complete",
            "deleted": "delete",
            "removed": "delete",
            "updated": "update",
            "listed": "list",
            "showing": "list",
        }

        # Check recent assistant messages
        for msg in reversed(history[-5:]):
            if msg.role == "assistant":
                content_lower = msg.content.lower()
                for keyword, action in action_keywords.items():
                    if keyword in content_lower:
                        return action

        return None

    def build_minimal_context(self, user_message: str) -> BuiltContext:
        """Build minimal context for a new conversation.

        Args:
            user_message: The user's message

        Returns:
            BuiltContext with just system prompt and user message
        """
        return self.execute(
            conversation_history=[],
            user_message=user_message,
            include_system_prompt=True
        )


# Singleton instance
context_builder = ContextBuilderSkill()
