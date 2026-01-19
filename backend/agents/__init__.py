"""Agents Module - Specialized AI agents for task management."""

from .base import BaseAgent, AgentResult
from .crud_agent import CRUDAgent
from .query_agent import QueryAgent
from .completion_agent import CompletionAgent
from .context_agent import ContextAgent
from .orchestrator import Orchestrator, OrchestrationResult, process_message

__all__ = [
    # Base
    "BaseAgent",
    "AgentResult",

    # Subagents
    "CRUDAgent",
    "QueryAgent",
    "CompletionAgent",
    "ContextAgent",

    # Orchestrator
    "Orchestrator",
    "OrchestrationResult",
    "process_message",
]
