"""Base Agent class for all subagents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    tool_used: Optional[str] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    """Abstract base class for all specialized agents.

    Agents are responsible for handling specific types of tasks:
    - CRUD Agent: Create, update, delete tasks
    - Query Agent: List and filter tasks
    - Completion Agent: Mark tasks as complete
    - Context Agent: Manage conversation context
    """

    name: str = "base_agent"
    description: str = "Base agent class"

    # Tools this agent can use
    available_tools: List[str] = []

    def __init__(self, user_id: str):
        """Initialize agent with user context.

        Args:
            user_id: The user ID for task operations
        """
        self.user_id = user_id

    @abstractmethod
    def can_handle(self, intent: str, **kwargs) -> bool:
        """Check if this agent can handle the given intent.

        Args:
            intent: The detected user intent
            **kwargs: Additional context

        Returns:
            True if this agent can handle the intent
        """
        pass

    @abstractmethod
    def execute(self, intent: str, **kwargs) -> AgentResult:
        """Execute the agent's task.

        Args:
            intent: The user's intent
            **kwargs: Additional parameters (parsed task, task_id, etc.)

        Returns:
            AgentResult with success status and message
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} for user={self.user_id}>"
