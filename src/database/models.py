import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, LargeBinary, Integer, Float
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from src.utils.crypto import encrypt_key, decrypt_key

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    tier = Column(String, default="free", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    encrypted_openai_api_key = Column(LargeBinary, nullable=True)
    encrypted_anthropic_api_key = Column(LargeBinary, nullable=True)
    encrypted_gemini_api_key = Column(LargeBinary, nullable=True)
    encrypted_groq_api_key = Column(LargeBinary, nullable=True)

    api_keys = relationship("APIKey", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")

    def set_byok(self, platform: str, api_key: str):
        encrypted_key = encrypt_key(api_key)
        setattr(self, f"encrypted_{platform}_api_key", encrypted_key)

    def get_byok(self, platform: str) -> str | None:
        encrypted_key = getattr(self, f"encrypted_{platform}_api_key")
        return decrypt_key(encrypted_key) if encrypted_key else None

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="api_keys")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    cost = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="usage_logs")
