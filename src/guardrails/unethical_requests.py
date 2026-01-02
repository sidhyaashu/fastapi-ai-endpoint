from typing import List
from .base import Guardrail, GuardrailResult
from src.schema import Message

# List of keywords that might indicate an unethical request
UNETHICAL_KEYWORDS = [
    "illegal", "hacking", "malware", "phishing", "hate speech", "violence", "self-harm",
]

class UnethicalRequestGuardrail(Guardrail):
    """
    A guardrail to detect unethical or harmful user requests.
    """

    async def check(self, messages: List[Message]) -> GuardrailResult:
        """
        Checks for keywords related to unethical requests in user messages.
        """
        for message in messages:
            if message.role == "user":
                for keyword in UNETHICAL_KEYWORDS:
                    if keyword in message.content.lower():
                        return GuardrailResult(
                            is_triggered=True,
                            risk_score=0.95,
                            message=f"Detected potentially unethical request containing '{keyword}'.",
                        )
        return GuardrailResult(is_triggered=False, risk_score=0.0)
