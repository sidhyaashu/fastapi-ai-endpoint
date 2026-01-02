import re
from typing import List
from .base import Guardrail, GuardrailResult
from src.schema import Message

# Basic regex for common PII
PII_PATTERNS = {
    "CREDIT_CARD": r"\\b(?:\\d[ -]*?){13,16}\\b",
    "SSN": r"\\b\\d{3}-\\d{2}-\\d{4}\\b",
    "EMAIL": r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b",
}

class SensitiveDataGuardrail(Guardrail):
    """
    A guardrail to detect sensitive data in the conversation.
    """

    async def check(self, messages: List[Message]) -> GuardrailResult:
        """
        Checks for sensitive data in the conversation using regex patterns.
        """
        for message in messages:
            if message.role == "user":
                for pii_type, pattern in PII_PATTERNS.items():
                    if re.search(pattern, message.content):
                        return GuardrailResult(
                            is_triggered=True,
                            risk_score=0.9,
                            message=f"Detected potential {pii_type} in user message.",
                        )
        return GuardrailResult(is_triggered=False, risk_score=0.0)
