"""Context Agent - Handles conversation context and general queries."""

from typing import Optional, List

from .base import BaseAgent, AgentResult
from mcp_server import list_tasks, ListTasksInput
from skills import context_builder, MessageContext


class ContextAgent(BaseAgent):
    """Agent for handling conversation context and general queries.

    Handles intents:
    - Greetings (hi, hello, hey)
    - Help requests
    - General questions about capabilities
    - Context-dependent references ("that task", "the last one")
    """

    name = "context_agent"
    description = "Handles conversation context and general queries"
    available_tools = ["list_tasks"]

    # Intent mappings
    GREETING_INTENTS = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    HELP_INTENTS = ["help", "what can you do", "how do i", "how to", "capabilities"]
    CONTEXT_INTENTS = ["that", "this", "it", "the one", "last", "previous"]

    def can_handle(self, intent: str, **kwargs) -> bool:
        """Check if this agent handles the given intent."""
        intent_lower = intent.lower()

        # Check for greetings
        if any(g in intent_lower for g in self.GREETING_INTENTS):
            return True

        # Check for help requests
        if any(h in intent_lower for h in self.HELP_INTENTS):
            return True

        # This agent has lowest priority for context references
        # Other agents should handle specific operations first
        return False

    def execute(self, intent: str, **kwargs) -> AgentResult:
        """Execute the context operation.

        Args:
            intent: The user's intent
            **kwargs: Additional parameters:
                - conversation_history: Previous messages

        Returns:
            AgentResult with response
        """
        intent_lower = intent.lower()

        # Handle greetings
        if any(g in intent_lower for g in self.GREETING_INTENTS):
            return self._handle_greeting(**kwargs)

        # Handle help requests
        if any(h in intent_lower for h in self.HELP_INTENTS):
            return self._handle_help(**kwargs)

        # Default contextual response
        return self._handle_general(**kwargs)

    def _handle_greeting(self, **kwargs) -> AgentResult:
        """Handle greeting messages."""
        # Get task summary for personalized greeting
        try:
            result = list_tasks(ListTasksInput(
                user_id=self.user_id,
                status="pending"
            ))
            pending_count = result.count

            if pending_count == 0:
                message = "Hello! You're all caught up - no pending tasks. Would you like to add something new?"
            elif pending_count == 1:
                message = f"Hello! You have 1 pending task. Would you like to see it or add more?"
            else:
                message = f"Hello! You have {pending_count} pending tasks. Would you like to see them?"

        except Exception:
            message = "Hello! How can I help you with your tasks today?"

        return AgentResult(
            success=True,
            message=message,
            data={"type": "greeting"}
        )

    def _handle_help(self, **kwargs) -> AgentResult:
        """Handle help requests."""
        help_message = """I'm your task management assistant. Here's what I can help you with:

**Adding Tasks**
- "Add a task to buy groceries"
- "Create a new task called finish report"
- "Remind me to call mom"

**Viewing Tasks**
- "Show my tasks"
- "What's left to do?" (pending tasks)
- "Show completed tasks"

**Completing Tasks**
- "Mark task 1 as done"
- "Complete the groceries task"
- "I finished the report"

**Updating Tasks**
- "Update task 1 title to new title"
- "Change the description of task 2"

**Deleting Tasks**
- "Delete task 3"
- "Remove the groceries task"

Just tell me what you'd like to do!"""

        return AgentResult(
            success=True,
            message=help_message,
            data={"type": "help"}
        )

    def _handle_general(self, **kwargs) -> AgentResult:
        """Handle general context-dependent queries."""
        message = "I'm here to help with your tasks. You can ask me to add, list, complete, update, or delete tasks. What would you like to do?"

        return AgentResult(
            success=True,
            message=message,
            data={"type": "general"}
        )

    def get_conversation_summary(self, conversation_history: List[MessageContext]) -> str:
        """Get a summary of the conversation context.

        Args:
            conversation_history: List of previous messages

        Returns:
            Summary string
        """
        if not conversation_history:
            return "This is the start of our conversation."

        # Use context builder to extract info
        built = context_builder.execute(
            conversation_history=conversation_history,
            user_message="",
            include_system_prompt=False
        )

        parts = []
        if built.recent_task_ids:
            parts.append(f"Recently mentioned tasks: {built.recent_task_ids}")
        if built.last_action:
            parts.append(f"Last action: {built.last_action}")

        return " | ".join(parts) if parts else "Conversation in progress."
