from typing import Dict, List, Optional
from uuid import uuid4
from src.schema import Message

class MemoryManager:
    """A simple in-memory store for conversation histories."""

    def __init__(self):
        self._store: Dict[str, List[Message]] = {}

    def get_history(self, conversation_id: str) -> List[Message]:
        """Retrieves the message history for a given conversation ID."""
        return self._store.get(conversation_id, [])

    def add_message(self, conversation_id: str, message: Message):
        """Adds a new message to the history of a conversation."""
        if conversation_id not in self._store:
            self._store[conversation_id] = []
        self._store[conversation_id].append(message)

    def generate_conversation_id(self) -> str:
        """Generates a new, unique conversation ID."""
        return str(uuid4())

# A global instance of the memory manager to be used by the application
memory_manager = MemoryManager()
