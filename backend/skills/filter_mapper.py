"""Filter Mapper Skill - Map natural language to filter parameters."""

import re
from typing import Literal
from dataclasses import dataclass

from .base import BaseSkill


@dataclass
class FilterParams:
    """Mapped filter parameters for list_tasks."""
    status: Literal["all", "pending", "completed"] = "all"
    confidence: float = 1.0


class FilterMapperSkill(BaseSkill):
    """Map natural language to task filter parameters.

    Examples:
        - "show my tasks" -> status="all"
        - "what's left to do" -> status="pending"
        - "show completed tasks" -> status="completed"
        - "what have I finished" -> status="completed"
        - "pending items" -> status="pending"
    """

    name = "filter_mapper"
    description = "Maps natural language to filter parameters"

    # Keywords indicating completed tasks
    COMPLETED_KEYWORDS = [
        r"\bcompleted?\b",
        r"\bfinished\b",
        r"\bdone\b",
        r"\bchecked\s*off\b",
        r"\bmarked\s*(?:as\s+)?(?:done|complete)\b",
        r"\baccomplished\b",
        r"\bwhat\s+(?:have\s+)?i\s+(?:have\s+)?(?:finished|completed|done)\b",
    ]

    # Keywords indicating pending/incomplete tasks
    PENDING_KEYWORDS = [
        r"\bpending\b",
        r"\bincomplete\b",
        r"\bunfinished\b",
        r"\boutstanding\b",
        r"\bremaining\b",
        r"\bleft\s+(?:to\s+do)?\b",
        r"\bto\s*-?\s*do\b",
        r"\bnot\s+(?:done|completed?|finished)\b",
        r"\bopen\b",
        r"\bactive\b",
        r"\bwhat(?:'s|\s+is)\s+left\b",
        r"\bwhat\s+(?:do\s+)?i\s+(?:still\s+)?(?:need|have)\s+to\s+do\b",
        r"\bwhat\s+(?:else\s+)?(?:do\s+)?i\s+need\s+to\b",
    ]

    # Keywords indicating all tasks
    ALL_KEYWORDS = [
        r"\ball\b",
        r"\beverything\b",
        r"\bfull\s+list\b",
        r"\bentire\b",
        r"\bwhole\b",
    ]

    def execute(self, user_input: str, **kwargs) -> FilterParams:
        """Map user input to filter parameters.

        Args:
            user_input: Natural language query about tasks

        Returns:
            FilterParams with mapped status filter
        """
        if not user_input:
            return FilterParams(status="all")

        text = user_input.lower().strip()

        # Check for explicit "all" keywords first
        for pattern in self.ALL_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                return FilterParams(status="all", confidence=0.95)

        # Check for completed keywords
        for pattern in self.COMPLETED_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                return FilterParams(status="completed", confidence=0.9)

        # Check for pending keywords
        for pattern in self.PENDING_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                return FilterParams(status="pending", confidence=0.9)

        # Default to "all" for generic queries
        return FilterParams(status="all", confidence=0.7)


# Singleton instance
filter_mapper = FilterMapperSkill()
