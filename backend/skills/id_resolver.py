"""ID Resolver Skill - Find task ID from description or context."""

import re
from typing import Optional, List
from dataclasses import dataclass

from .base import BaseSkill


@dataclass
class ResolvedTask:
    """Result of task ID resolution."""
    task_id: Optional[int] = None
    confidence: float = 0.0
    matched_title: Optional[str] = None
    resolution_method: str = "none"  # "exact_id", "title_match", "fuzzy", "none"


@dataclass
class TaskReference:
    """A task reference for matching."""
    id: int
    title: str
    completed: bool = False


class IDResolverSkill(BaseSkill):
    """Resolve task references to actual task IDs.

    Handles various ways users might refer to tasks:
    - Direct ID: "task 5", "task #5", "id 5"
    - By title: "the groceries task", "buy milk"
    - Ordinal: "first task", "last task", "second one"
    - Relative: "that task", "the one I just added"
    """

    name = "id_resolver"
    description = "Resolves task references to task IDs"

    # Patterns for direct ID extraction
    ID_PATTERNS = [
        r"(?:task|todo|item)?\s*#?\s*(\d+)",
        r"(?:id|number)\s*[:\-]?\s*(\d+)",
        r"#(\d+)",
    ]

    # Ordinal mappings
    ORDINALS = {
        "first": 0, "1st": 0,
        "second": 1, "2nd": 1,
        "third": 2, "3rd": 2,
        "fourth": 3, "4th": 3,
        "fifth": 4, "5th": 4,
        "last": -1,
        "latest": -1,
        "newest": -1,
        "most recent": -1,
    }

    def execute(
        self,
        user_input: str,
        tasks: List[TaskReference],
        **kwargs
    ) -> ResolvedTask:
        """Resolve a task reference to a task ID.

        Args:
            user_input: Natural language reference to a task
            tasks: List of available tasks to match against

        Returns:
            ResolvedTask with resolved ID or None if not found
        """
        if not user_input or not tasks:
            return ResolvedTask()

        text = user_input.lower().strip()

        # Try direct ID extraction first
        result = self._try_direct_id(text, tasks)
        if result.task_id is not None:
            return result

        # Try ordinal references
        result = self._try_ordinal(text, tasks)
        if result.task_id is not None:
            return result

        # Try title matching
        result = self._try_title_match(text, tasks)
        if result.task_id is not None:
            return result

        return ResolvedTask()

    def _try_direct_id(self, text: str, tasks: List[TaskReference]) -> ResolvedTask:
        """Try to extract a direct task ID from text."""
        for pattern in self.ID_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_id = int(match.group(1))
                # Verify the task exists
                for task in tasks:
                    if task.id == task_id:
                        return ResolvedTask(
                            task_id=task_id,
                            confidence=1.0,
                            matched_title=task.title,
                            resolution_method="exact_id"
                        )
        return ResolvedTask()

    def _try_ordinal(self, text: str, tasks: List[TaskReference]) -> ResolvedTask:
        """Try to resolve ordinal references like 'first task'."""
        for ordinal, index in self.ORDINALS.items():
            if ordinal in text:
                try:
                    if index == -1:
                        # Last/latest/newest
                        task = tasks[0]  # Assuming tasks are sorted newest first
                    else:
                        task = tasks[index]

                    return ResolvedTask(
                        task_id=task.id,
                        confidence=0.9,
                        matched_title=task.title,
                        resolution_method="ordinal"
                    )
                except IndexError:
                    pass
        return ResolvedTask()

    def _try_title_match(self, text: str, tasks: List[TaskReference]) -> ResolvedTask:
        """Try to match by task title using fuzzy matching."""
        best_match = None
        best_score = 0.0

        # Remove common words that don't help matching
        clean_text = self._remove_stop_words(text)

        for task in tasks:
            clean_title = self._remove_stop_words(task.title.lower())

            # Calculate similarity score
            score = self._calculate_similarity(clean_text, clean_title)

            if score > best_score and score >= 0.5:  # Minimum threshold
                best_score = score
                best_match = task

        if best_match:
            return ResolvedTask(
                task_id=best_match.id,
                confidence=best_score,
                matched_title=best_match.title,
                resolution_method="title_match"
            )

        return ResolvedTask()

    def _remove_stop_words(self, text: str) -> str:
        """Remove common stop words from text."""
        stop_words = {
            "the", "a", "an", "task", "todo", "item", "called", "named",
            "titled", "about", "for", "to", "my", "that", "this", "one",
            "please", "can", "you", "complete", "finish", "delete", "remove",
            "mark", "done", "update", "edit", "change"
        }
        words = text.split()
        return " ".join(w for w in words if w not in stop_words)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings."""
        if not text1 or not text2:
            return 0.0

        # Exact match
        if text1 == text2:
            return 1.0

        # Check if one contains the other
        if text1 in text2 or text2 in text1:
            return 0.9

        # Word overlap (Jaccard similarity)
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0


# Singleton instance
id_resolver = IDResolverSkill()
