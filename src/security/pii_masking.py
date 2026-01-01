import re
from typing import List
from src.schema import Message

# A simple regex for email addresses
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def mask_pii_in_text(text: str) -> str:
    """Masks email addresses in a given text."""
    return EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)

def mask_pii_in_messages(messages: List[Message]) -> List[Message]:
    """Applies PII masking to the content of each message in a list."""
    masked_messages = []
    for msg in messages:
        masked_content = mask_pii_in_text(msg.content)
        masked_messages.append(Message(role=msg.role, content=masked_content))
    return masked_messages
