import re
from typing import List
from .base import Guardrail, GuardrailResult
from src.schema import Message

# Very basic regex for SQL injection keywords
SQL_INJECTION_PATTERNS = [
    r"(?i)\\b(SELECT\\s.*\\sFROM|INSERT\\sINTO|UPDATE\\s.*\\sSET|DELETE\\sFROM|DROP\\sTABLE|UNION\\sSELECT)\\b"
]

class SQLInjectionGuardrail(Guardrail):
    """
    A guardrail to detect potential SQL injection attacks.
    """

    async def check(self, messages: List[Message]) -> GuardrailResult:
        """
        Checks for SQL injection patterns in user messages.
        """
        for message in messages:
            if message.role == "user":
                for pattern in SQL_INJECTION_PATTERNS:
                    if re.search(pattern, message.content):
                        return GuardrailResult(
                            is_triggered=True,
                            risk_score=0.9,
                            message="Detected potential SQL injection attempt.",
                        )
        return GuardrailResult(is_triggered=False, risk_score=0.0)
