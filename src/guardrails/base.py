from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from src.schema import Message

@dataclass
class GuardrailResult:
    is_triggered: bool
    risk_score: float
    message: str = ""

class Guardrail(ABC):
    """Abstract base class for an AI guardrail."""

    @abstractmethod
    async def check(self, messages: List[Message]) -> GuardrailResult:
        """
        Checks the conversation for a specific security or policy violation.

        Args:
            messages: The list of messages in the conversation.

        Returns:
            A GuardrailResult indicating whether the guardrail was triggered.
        """
        pass
