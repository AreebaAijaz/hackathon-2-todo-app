"""Base class for all skills."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseSkill(ABC):
    """Abstract base class for all skills.

    Skills are reusable components that perform specific tasks
    and can be shared across multiple agents.
    """

    name: str = "base_skill"
    description: str = "Base skill class"

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the skill with given parameters.

        Args:
            **kwargs: Skill-specific parameters

        Returns:
            Skill-specific output
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
