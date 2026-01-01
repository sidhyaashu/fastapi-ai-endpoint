from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.database.models import Conversation, Message as DBMessage
from src.schema import Message
from fastapi import Depends

class MemoryManager:
    """Manages conversation histories in the database."""

    def __init__(self, db: Session):
        self.db = db

    def get_history(self, conversation_id: str) -> List[Message]:
        """Retrieves the message history for a given conversation ID."""
        db_messages = self.db.query(DBMessage).filter(DBMessage.conversation_id == conversation_id).order_by(DBMessage.created_at).all()
        return [Message(role=msg.role, content=msg.content) for msg in db_messages]

    def add_message(self, conversation_id: str, message: Message, user_id: str):
        """Adds a new message to the history of a conversation."""
        conversation = self.db.query(Conversation).filter_by(id=conversation_id).first()
        if not conversation:
            conversation = Conversation(id=conversation_id, user_id=user_id)
            self.db.add(conversation)
            self.db.commit()

        db_message = DBMessage(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content
        )
        self.db.add(db_message)
        self.db.commit()

    def generate_conversation_id(self) -> str:
        """Generates a new, unique conversation ID."""
        return str(uuid4())

def get_memory_manager(db: Session = Depends(get_db)):
    """FastAPI dependency to get a memory manager instance."""
    return MemoryManager(db)
