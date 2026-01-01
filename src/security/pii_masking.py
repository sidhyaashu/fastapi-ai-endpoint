from typing import List
from functools import lru_cache
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from src.schema import Message

@lru_cache(maxsize=1)
def get_presidio_analyzer() -> AnalyzerEngine:
    """Initializes and returns a cached Presidio AnalyzerEngine."""
    # This can be configured to load a specific NER model or language
    return AnalyzerEngine()

@lru_cache(maxsize=1)
def get_presidio_anonymizer() -> AnonymizerEngine:
    """Initializes and returns a cached Presidio AnonymizerEngine."""
    return AnonymizerEngine()

def mask_pii_in_text(text: str) -> str:
    """
    Analyzes text for PII and returns an anonymized version.
    Uses Presidio for robust PII detection and masking.
    """
    analyzer = get_presidio_analyzer()
    anonymizer = get_presidio_anonymizer()

    # Analyze the text to find PII entities
    analyzer_results = analyzer.analyze(text=text, language="en")

    # Anonymize the detected entities
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators={"DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"})}
    )

    return anonymized_result.text

def mask_pii_in_messages(messages: List[Message]) -> List[Message]:
    """Applies PII masking to the content of each message in a list."""
    masked_messages = []
    for msg in messages:
        masked_content = mask_pii_in_text(msg.content)
        masked_messages.append(Message(role=msg.role, content=masked_content))
    return masked_messages
