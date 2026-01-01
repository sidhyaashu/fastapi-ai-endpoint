from typing import Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str 
    platform: Optional[str] = None

class ChatResponse(BaseModel):
    response: str