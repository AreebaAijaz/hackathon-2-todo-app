"""Task Parser Skill - Extract task details from natural language."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from .base import BaseSkill


class ParsedTask:
    """Represents a parsed task from natural language."""

    def __init__(
        self,
        title: str = "",
        description: Optional[str] = None,
        has_title: bool = True,
        priority: str = "medium",
        tags: Optional[List[str]] = None,
        due_date: Optional[str] = None,
        recurring_pattern: str = "none",
    ):
        self.title = title
        self.description = description
        self.has_title = has_title
        self.priority = priority
        self.tags = tags or []
        self.due_date = due_date
        self.recurring_pattern = recurring_pattern


class TaskParserSkill(BaseSkill):
    """Extract task title and description from natural language input.

    Enhanced to also extract priority, tags, due dates, and recurring patterns.

    Examples:
        - "add high priority task buy groceries tagged shopping due friday" ->
          title="Buy groceries", priority="high", tags=["shopping"], due_date="2026-02-13T23:59:00Z"
        - "create urgent task call dentist every week" ->
          title="Call dentist", priority="urgent", recurring_pattern="weekly"
    """

    name = "task_parser"
    description = "Extracts task details from natural language including priority, tags, due dates, and recurring patterns"

    # Patterns to remove from the beginning of user input
    PREFIXES = [
        r"^(?:please\s+)?(?:can you\s+)?(?:could you\s+)?",
        r"^(?:i want to\s+|i need to\s+|i'd like to\s+)?",
        r"^(?:add|create|make|new)\s+(?:a\s+)?(?:new\s+)?(?:task|todo|item)\s*",
        r"^(?:task|todo)\s*:?\s*",
        r"^(?:remind me to\s+|don't forget to\s+|remember to\s+)",
        r"^(?:called|named|titled)\s+",
    ]

    # Priority extraction patterns
    PRIORITY_PATTERNS = [
        (r"\b(?:urgent|urgently|asap|immediately|critical)\b", "urgent"),
        (r"\bhigh\s*(?:priority|pri|importance)\b", "high"),
        (r"\b(?:priority|pri)\s*:?\s*high\b", "high"),
        (r"\bimportant\b", "high"),
        (r"\blow\s*(?:priority|pri|importance)\b", "low"),
        (r"\b(?:priority|pri)\s*:?\s*low\b", "low"),
        (r"\bmedium\s*(?:priority|pri|importance)\b", "medium"),
        (r"\b(?:priority|pri)\s*:?\s*medium\b", "medium"),
        (r"\b(?:priority|pri)\s*:?\s*urgent\b", "urgent"),
    ]

    # Tag extraction patterns
    TAG_PATTERNS = [
        r"#(\w[\w-]*)",                                     # #shopping, #work-stuff
        r"\btagged\s+(\w[\w-]*(?:\s*,\s*\w[\w-]*)*)",       # tagged work, tagged work,personal
        r"\btag\s+(\w[\w-]*(?:\s*,\s*\w[\w-]*)*)",          # tag work, tag work,personal
        r"\btags?\s*:\s*(\w[\w-]*(?:\s*,\s*\w[\w-]*)*)",    # tag: work, tags: work,personal
    ]

    # Recurring pattern extraction
    RECURRING_PATTERNS = [
        (r"\b(?:every\s*day|daily|each\s*day)\b", "daily"),
        (r"\b(?:every\s*week|weekly|each\s*week)\b", "weekly"),
        (r"\b(?:every\s*month|monthly|each\s*month)\b", "monthly"),
        (r"\b(?:recurring|repeat(?:s|ing)?)\s+(?:daily|every\s*day)\b", "daily"),
        (r"\b(?:recurring|repeat(?:s|ing)?)\s+(?:weekly|every\s*week)\b", "weekly"),
        (r"\b(?:recurring|repeat(?:s|ing)?)\s+(?:monthly|every\s*month)\b", "monthly"),
    ]

    # Due date patterns
    DUE_DATE_PATTERNS = [
        r"\b(?:due|by|before|until|deadline)\s+(.+?)(?:\s+(?:tagged?|tag:|#|priority|pri|every|daily|weekly|monthly|recurring|repeat)|\s*$)",
        r"\b(?:due|by|before)\s*:?\s*(.+?)(?:\s+(?:tagged?|tag:|#|priority|pri|every|daily|weekly|monthly|recurring|repeat)|\s*$)",
    ]

    # Day name to offset mapping
    DAY_NAMES = {
        "monday": 0, "mon": 0,
        "tuesday": 1, "tue": 1, "tues": 1,
        "wednesday": 2, "wed": 2,
        "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
        "friday": 4, "fri": 4,
        "saturday": 5, "sat": 5,
        "sunday": 6, "sun": 6,
    }

    # Description patterns
    DESCRIPTION_PATTERNS = [
        r"(?:with\s+)?(?:description|desc|details?|note)\s*[:\-]?\s*(.+?)(?:\s+(?:tagged?|tag:|#|priority|pri|due|by|every|daily|weekly|monthly)|\s*$)",
        r"\s+-\s+(.+?)(?:\s+(?:tagged?|tag:|#|priority|pri|due|by|every|daily|weekly|monthly)|\s*$)",
        r"\s+\((.+?)\)",
    ]

    def execute(self, user_input: str, **kwargs) -> ParsedTask:
        """Parse task details from user input.

        Args:
            user_input: Natural language input from user

        Returns:
            ParsedTask with extracted title, priority, tags, due_date, recurring_pattern
        """
        if not user_input or not user_input.strip():
            return ParsedTask(title="", has_title=False)

        text = user_input.strip()

        # Extract structured fields first (before modifying text)
        priority = self._extract_priority(text)
        tags = self._extract_tags(text)
        recurring = self._extract_recurring(text)
        due_date = self._extract_due_date(text)
        description = None

        # Remove extracted metadata from text to get clean title
        clean = text

        # Remove priority phrases
        for pattern, _ in self.PRIORITY_PATTERNS:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

        # Remove tag phrases (including standalone # symbols left over)
        for pattern in self.TAG_PATTERNS:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s*#\s*', ' ', clean)

        # Remove recurring phrases
        for pattern, _ in self.RECURRING_PATTERNS:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

        # Remove due date phrases
        for pattern in self.DUE_DATE_PATTERNS:
            match = re.search(pattern, clean, re.IGNORECASE)
            if match:
                clean = clean[:match.start()] + clean[match.end():]

        # Try to extract description
        for pattern in self.DESCRIPTION_PATTERNS:
            match = re.search(pattern, clean, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                clean = clean[:match.start()].strip()
                break

        # Remove common prefixes
        for pattern in self.PREFIXES:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE).strip()

        # Clean up the title
        title = self._clean_title(clean)

        if not title:
            return ParsedTask(title="", has_title=False)

        return ParsedTask(
            title=title,
            description=description,
            has_title=True,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurring_pattern=recurring,
        )

    def _extract_priority(self, text: str) -> str:
        """Extract priority level from text."""
        for pattern, priority in self.PRIORITY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return priority
        return "medium"

    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text."""
        tags = set()
        for pattern in self.TAG_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                raw = match.group(1)
                for tag in raw.split(","):
                    tag = tag.strip().lower()
                    if tag and re.match(r"^[a-zA-Z0-9_-]+$", tag):
                        tags.add(tag)
        return sorted(tags)[:10]

    def _extract_recurring(self, text: str) -> str:
        """Extract recurring pattern from text."""
        for pattern, recurrence in self.RECURRING_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return recurrence
        return "none"

    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract due date from text and return ISO 8601 string."""
        for pattern in self.DUE_DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                parsed = self._parse_date_string(date_str)
                if parsed:
                    return parsed
        return None

    def _parse_date_string(self, date_str: str) -> Optional[str]:
        """Parse a natural language date string to ISO 8601."""
        text = date_str.lower().strip()
        now = datetime.now(timezone.utc)

        # "today"
        if text == "today":
            target = now.replace(hour=23, minute=59, second=0, microsecond=0)
            return target.isoformat()

        # "tomorrow"
        if text == "tomorrow":
            target = (now + timedelta(days=1)).replace(hour=23, minute=59, second=0, microsecond=0)
            return target.isoformat()

        # "next week"
        if text in ("next week",):
            target = (now + timedelta(days=7)).replace(hour=23, minute=59, second=0, microsecond=0)
            return target.isoformat()

        # Day names: "friday", "next friday"
        is_next = text.startswith("next ")
        day_text = text.replace("next ", "").strip()
        if day_text in self.DAY_NAMES:
            target_day = self.DAY_NAMES[day_text]
            current_day = now.weekday()
            days_ahead = target_day - current_day
            if days_ahead <= 0:
                days_ahead += 7
            if is_next and days_ahead <= 7:
                days_ahead += 7
            target = (now + timedelta(days=days_ahead)).replace(hour=23, minute=59, second=0, microsecond=0)
            return target.isoformat()

        # Try ISO format directly
        try:
            parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return parsed.isoformat()
        except ValueError:
            pass

        # Try common date formats
        for fmt in ("%b %d", "%B %d", "%m/%d", "%m-%d", "%b %d %Y", "%B %d %Y", "%m/%d/%Y"):
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                if parsed.year == 1900:
                    parsed = parsed.replace(year=now.year)
                    if parsed.replace(tzinfo=timezone.utc) < now:
                        parsed = parsed.replace(year=now.year + 1)
                target = parsed.replace(hour=23, minute=59, second=0, microsecond=0, tzinfo=timezone.utc)
                return target.isoformat()
            except ValueError:
                continue

        return None

    def _clean_title(self, text: str) -> str:
        """Clean up the extracted title."""
        # Remove leading/trailing punctuation and extra whitespace
        text = re.sub(r'^[\s\-:,]+|[\s\-:,]+$', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

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
