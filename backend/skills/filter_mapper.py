"""Filter Mapper Skill - Map natural language to filter parameters."""

import re
from typing import Optional, List, Literal
from dataclasses import dataclass, field

from .base import BaseSkill


@dataclass
class FilterParams:
    """Mapped filter parameters for list_tasks."""
    status: Literal["all", "pending", "completed"] = "all"
    priority: Optional[str] = None
    tags: Optional[str] = None
    overdue: Optional[bool] = None
    search: Optional[str] = None
    sort_by: str = "created_at"
    confidence: float = 1.0


class FilterMapperSkill(BaseSkill):
    """Map natural language to task filter parameters.

    Enhanced to support priority, tags, overdue, and search filters.

    Examples:
        - "show my tasks" -> status="all"
        - "show urgent tasks" -> priority="urgent"
        - "what's overdue" -> overdue=True
        - "show my work tasks" -> tags="work"
        - "find groceries" -> search="groceries"
        - "show high priority work tasks" -> priority="high", tags="work"
    """

    name = "filter_mapper"
    description = "Maps natural language to filter parameters including priority, tags, overdue, and search"

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

    # Priority filter patterns
    PRIORITY_PATTERNS = [
        (r"\burgent\b", "urgent"),
        (r"\bhigh\s*(?:priority|pri)?\b", "high"),
        (r"\blow\s*(?:priority|pri)?\b", "low"),
        (r"\bmedium\s*(?:priority|pri)?\b", "medium"),
        (r"\bcritical\b", "urgent"),
        (r"\bimportant\b", "high"),
    ]

    # Overdue patterns
    OVERDUE_KEYWORDS = [
        r"\boverdue\b",
        r"\bpast\s*due\b",
        r"\blate\b",
        r"\bmissed\s*deadline\b",
        r"\bexpired\b",
    ]

    # Search patterns
    SEARCH_PATTERNS = [
        r"\b(?:find|search|look\s+for|search\s+for)\s+['\"]?(.+?)['\"]?\s*$",
        r"\b(?:find|search|look\s+for|search\s+for)\s+['\"]?(.+?)['\"]?(?:\s+in\s+|\s+from\s+)",
    ]

    # Tag filter patterns
    TAG_FILTER_PATTERNS = [
        r"#(\w[\w-]*)",
        r"\btagged?\s+(\w[\w,-]*)",
        r"\b(\w+)\s+tasks?\b",  # "work tasks", "personal tasks"
    ]

    # Common words that are NOT tags (to avoid false positives)
    NON_TAG_WORDS = {
        "my", "all", "the", "show", "list", "get", "what", "how", "many",
        "pending", "completed", "done", "finished", "open", "active",
        "urgent", "high", "medium", "low", "priority", "overdue", "late",
        "important", "critical", "new", "old", "recent", "some", "any",
        "these", "those", "other", "remaining", "outstanding", "incomplete",
    }

    def execute(self, user_input: str, **kwargs) -> FilterParams:
        """Map user input to filter parameters.

        Args:
            user_input: Natural language query about tasks

        Returns:
            FilterParams with mapped filters
        """
        if not user_input:
            return FilterParams(status="all")

        text = user_input.lower().strip()
        params = FilterParams()

        # Check for overdue
        for pattern in self.OVERDUE_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                params.overdue = True
                params.status = "pending"
                params.confidence = 0.9
                break

        # Check for priority filter
        if not params.overdue:
            for pattern, priority in self.PRIORITY_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    # Avoid matching "high" in "highlight" etc
                    if priority == "high" and re.search(r"\bhigh(?:light|er|est|ly)\b", text):
                        continue
                    params.priority = priority
                    params.confidence = 0.85
                    break

        # Check for search query
        for pattern in self.SEARCH_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                params.search = match.group(1).strip()
                params.confidence = 0.9
                break

        # Check for tag filter (only from explicit tag references)
        for pattern in self.TAG_FILTER_PATTERNS[:2]:  # Only hashtag and "tagged X"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw = match.group(1)
                tags = [t.strip().lower() for t in raw.split(",") if t.strip()]
                tags = [t for t in tags if t not in self.NON_TAG_WORDS]
                if tags:
                    params.tags = ",".join(tags)
                    params.confidence = 0.85
                    break

        # Check "<word> tasks" pattern more carefully
        if not params.tags:
            match = re.search(r"\b(\w+)\s+tasks?\b", text, re.IGNORECASE)
            if match:
                word = match.group(1).lower()
                if word not in self.NON_TAG_WORDS and len(word) > 2:
                    params.tags = word
                    params.confidence = 0.7

        # Status filter (only if not already set by overdue)
        if not params.overdue:
            # Check for explicit "all" keywords first
            for pattern in self.ALL_KEYWORDS:
                if re.search(pattern, text, re.IGNORECASE):
                    params.status = "all"
                    if params.confidence > 0.9:
                        params.confidence = 0.95
                    break

            # Check for completed keywords
            for pattern in self.COMPLETED_KEYWORDS:
                if re.search(pattern, text, re.IGNORECASE):
                    params.status = "completed"
                    params.confidence = max(params.confidence, 0.9)
                    break

            # Check for pending keywords
            for pattern in self.PENDING_KEYWORDS:
                if re.search(pattern, text, re.IGNORECASE):
                    params.status = "pending"
                    params.confidence = max(params.confidence, 0.9)
                    break

        # Sort by priority if priority filter is active
        if params.priority:
            params.sort_by = "priority"

        return params


# Singleton instance
filter_mapper = FilterMapperSkill()
