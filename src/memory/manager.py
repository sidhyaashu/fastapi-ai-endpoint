from typing import List
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.session import get_db
from src.database.models import Conversation, Message as DBMessage
from src.schema import Message
from fastapi import Depends

class MemoryManager:
    """Manages conversation histories in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_history(self, conversation_id: str) -> List[Message]:
        """Retrieves the message history for a given conversation ID."""
        result = await self.db.execute(
            select(DBMessage)
            .where(DBMessage.conversation_id == conversation_id)
            .order_by(DBMessage.created_at)
        )
        db_messages = result.scalars().all()
        return [Message(role=msg.role, content=msg.content) for msg in db_messages]

    async def add_message(self, conversation_id: str, message: Message, user_id: str):
        """Adds a new message to the history of a conversation."""
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conversation = result.scalars().first()

        if not conversation:
            conversation = Conversation(id=conversation_id, user_id=user_id)
            self.db.add(conversation)
            await self.db.commit()

        db_message = DBMessage(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content
        )
        self.db.add(db_message)
        await self.db.commit()

    def generate_conversation_id(self) -> str:
        """Generates a new, unique conversation ID."""
        return str(uuid4())

async def get_memory_manager(db: AsyncSession = Depends(get_db)):
    """FastAPI dependency to get a memory manager instance."""
    return MemoryManager(db)
