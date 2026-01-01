from typing import Dict, List, Optional
from src.schema import Message

class CacheManager:
    """A simple in-memory cache for chat responses."""

    def __init__(self):
        self._store: Dict[str, str] = {}

    def _generate_key(self, messages: List[Message]) -> str:
        """Generates a cache key from a list of messages."""
        return "".join([f"{m.role}:{m.content}" for m in messages])

    def get(self, messages: List[Message]) -> Optional[str]:
        """Retrieves a cached response."""
        key = self._generate_key(messages)
        return self._store.get(key)

    def set(self, messages: List[Message], response: str):
        """Stores a response in the cache."""
        key = self._generate_key(messages)
        self._store[key] = response

# A global instance of the cache manager
cache_manager = CacheManager()
