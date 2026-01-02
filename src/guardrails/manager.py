from typing import List
from functools import lru_cache
from .base import Guardrail, GuardrailResult
from .sensitive_data import SensitiveDataGuardrail
from .sql_injection import SQLInjectionGuardrail
from .unethical_requests import UnethicalRequestGuardrail
from .jailbreak import JailbreakGuardrail
from src.schema import Message
from src.utils.logger import logger
from src import config

class GuardrailManager:
    def __init__(self):
        self._guardrails: List[Guardrail] = self._load_guardrails()

    def _load_guardrails(self) -> List[Guardrail]:
        """Loads all available guardrails."""
        return [
            SensitiveDataGuardrail(),
            SQLInjectionGuardrail(),
            UnethicalRequestGuardrail(),
            JailbreakGuardrail(),
        ]

    async def scan(self, messages: List[Message]) -> GuardrailResult:
        """
        Scans the conversation against all loaded guardrails.

        Args:
            messages: The list of messages in the conversation.

        Returns:
            An aggregated GuardrailResult. If any guardrail is triggered,
            this returns the result of the first triggered guardrail.
        """
        for guardrail in self._guardrails:
            result = await guardrail.check(messages)
            if result.is_triggered:
                logger.warn(
                    "Guardrail triggered",
                    guardrail=guardrail.__class__.__name__,
                    message=result.message,
                    risk_score=result.risk_score,
                )
                if result.risk_score >= config.GUARDRAIL_BLOCK_THRESHOLD:
                    return result

        return GuardrailResult(is_triggered=False, risk_score=0.0)

@lru_cache(maxsize=1)
def get_guardrail_manager() -> GuardrailManager:
    return GuardrailManager()
