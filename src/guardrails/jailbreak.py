from typing import List
import re
from .base import Guardrail, GuardrailResult
from src.schema import Message

# Common jailbreak patterns
JAILBREAK_PATTERNS = [
    r"(?i)ignore previous instructions",
    r"(?i)act as if",
    r"(?i)you are an unfiltered assistant",
    r"(?i)DAN",
    r"(?i)developer mode",
    r"(?i)AIM",
]

class JailbreakGuardrail(Guardrail):
    """
    A guardrail to detect attempts to jailbreak the AI.
    """

    async def check(self, messages: List[Message]) -> GuardrailResult:
        """
        Checks for common jailbreak patterns in user messages.
        """
        for message in messages:
            if message.role == "user":
                for pattern in JAILBREAK_PATTERNS:
                    if re.search(pattern, message.content):
                        return GuardrailResult(
                            is_triggered=True,
                            risk_score=1.0,
                            message="Detected potential jailbreak attempt.",
                        )
        return GuardrailResult(is_triggered=False, risk_score=0.0)
