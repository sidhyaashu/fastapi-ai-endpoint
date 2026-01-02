from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pgvector.sqlalchemy import Vector
from src.database.models import SemanticCache
from src.schema import Message
from src.utils.embedding import get_embedding
from fastapi import Depends
from src.database.session import get_db

class CacheManager:
    """A database-backed semantic cache for chat responses."""

    def __init__(self, db: AsyncSession, similarity_threshold: float = 0.9):
        self.db = db
        self.similarity_threshold = similarity_threshold

    async def get(self, messages: List[Message]) -> Optional[str]:
        """
        Retrieves a cached response by finding a semantically similar prompt.
        """
        last_user_message = next((msg.content for msg in reversed(messages) if msg.role == 'user'), None)
        if not last_user_message:
            return None

        embedding = get_embedding(last_user_message)

        # Find the closest matching embedding in the database
        result = await self.db.execute(
            select(SemanticCache)
            .order_by(SemanticCache.embedding.l2_distance(embedding))
            .limit(1)
        )
        closest_match = result.scalars().first()

        if closest_match:
            # Check if the similarity is within the threshold
            distance = await self.db.execute(
                select(SemanticCache.embedding.l2_distance(embedding))
                .where(SemanticCache.id == closest_match.id)
            )
            if distance.scalar_one() < (1 - self.similarity_threshold):
                return closest_match.response

        return None

    async def set(self, messages: List[Message], response: str):
        """Stores a prompt-response pair and its embedding in the cache."""
        last_user_message = next((msg.content for msg in reversed(messages) if msg.role == 'user'), None)
        if not last_user_message:
            return

        embedding = get_embedding(last_user_message)

        cache_entry = SemanticCache(
            prompt=last_user_message,
            response=response,
            embedding=embedding
        )
        self.db.add(cache_entry)
        await self.db.commit()

async def get_cache_manager(db: AsyncSession = Depends(get_db)):
    """FastAPI dependency to get a cache manager instance."""
    return CacheManager(db)
