"""Task Parser Skill - Extract task details from natural language."""

import re
from typing import Optional
from dataclasses import dataclass

from .base import BaseSkill


@dataclass
class ParsedTask:
    """Represents a parsed task from natural language."""
    title: str
    description: Optional[str] = None
    has_title: bool = True


class TaskParserSkill(BaseSkill):
    """Extract task title and description from natural language input.

    Examples:
        - "add task buy groceries" -> title="buy groceries"
        - "create a task called meeting with john" -> title="meeting with john"
        - "remind me to call mom" -> title="call mom"
        - "add buy milk with description get 2% milk" -> title="buy milk", desc="get 2% milk"
    """

    name = "task_parser"
    description = "Extracts task title and description from natural language"

    # Patterns to remove from the beginning of user input
    PREFIXES = [
        r"^(?:please\s+)?(?:can you\s+)?(?:could you\s+)?",
        r"^(?:i want to\s+|i need to\s+|i'd like to\s+)?",
        r"^(?:add|create|make|new)\s+(?:a\s+)?(?:new\s+)?(?:task|todo|item)\s*",
        r"^(?:task|todo)\s*:?\s*",
        r"^(?:remind me to\s+|don't forget to\s+|remember to\s+)",
        r"^(?:called|named|titled)\s+",
    ]

    # Patterns to extract description
    DESCRIPTION_PATTERNS = [
        r"(?:with\s+)?(?:description|desc|details?|note)\s*[:\-]?\s*(.+)$",
        r"\s+-\s+(.+)$",  # "buy milk - get 2% milk"
        r"\s+\((.+)\)$",  # "buy milk (get 2% milk)"
    ]

    def execute(self, user_input: str, **kwargs) -> ParsedTask:
        """Parse task details from user input.

        Args:
            user_input: Natural language input from user

        Returns:
            ParsedTask with extracted title and optional description
        """
        if not user_input or not user_input.strip():
            return ParsedTask(title="", has_title=False)

        text = user_input.strip()
        description = None

        # Try to extract description first
        for pattern in self.DESCRIPTION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                text = text[:match.start()].strip()
                break

        # Remove common prefixes
        for pattern in self.PREFIXES:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

        # Clean up the title
        title = self._clean_title(text)

        if not title:
            return ParsedTask(title="", has_title=False)

        return ParsedTask(
            title=title,
            description=description,
            has_title=True
        )

    def _clean_title(self, text: str) -> str:
        """Clean up the extracted title."""
        # Remove leading/trailing punctuation
        text = re.sub(r'^[\s\-:,]+|[\s\-:,]+$', '', text)

        # Remove quotes if they wrap the entire title
        if len(text) >= 2:
            if (text[0] == '"' and text[-1] == '"') or \
               (text[0] == "'" and text[-1] == "'"):
                text = text[1:-1]

        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        return text.strip()


# Singleton instance
task_parser = TaskParserSkill()
