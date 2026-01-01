from typing import List, Optional
import redis
import hashlib
from src import config
from src.schema import Message

class CacheManager:
    """A Redis-based cache for chat responses with a TTL."""

    def __init__(self, redis_url: str, ttl: int = 3600):
        """
        Initializes the CacheManager with a Redis connection.
        Args:
            redis_url (str): The connection URL for the Redis server.
            ttl (int): The default time-to-live for cache entries in seconds.
        """
        self.client = redis.from_url(redis_url)
        self.ttl = ttl

    def _generate_key(self, messages: List[Message]) -> str:
        """Generates a SHA-256 hash key from a list of messages for consistent key format."""
        content = "".join([f"{m.role}:{m.content}" for m in messages])
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get(self, messages: List[Message]) -> Optional[str]:
        """Retrieves a cached response from Redis."""
        key = self._generate_key(messages)
        cached_response = self.client.get(key)
        return cached_response.decode('utf-8') if cached_response else None

    def set(self, messages: List[Message], response: str):
        """Stores a response in the Redis cache with a TTL."""
        key = self._generate_key(messages)
        self.client.set(key, response, ex=self.ttl)

# A global instance of the cache manager, configured from src.config
cache_manager = CacheManager(redis_url=config.REDIS_URL)
