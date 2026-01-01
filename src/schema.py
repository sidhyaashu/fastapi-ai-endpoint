from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Core Message and Conversation Structures ---

class Message(BaseModel):
    """Represents a single message in the conversation."""
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant').")
    content: str = Field(..., description="The text content of the message.")

class ModelParameters(BaseModel):
    """Hyperparameters to control the AI model's generation process."""
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Controls randomness. Lower is more deterministic.")
    max_tokens: Optional[int] = Field(None, gt=0, description="The maximum number of tokens to generate.")

# --- Request Models ---

class ChatRequest(BaseModel):
    """The main request model for the /chat endpoint."""
    messages: List[Message] = Field(..., description="A list of messages forming the conversation history.")
    platform: Optional[str] = Field(None, description="The AI platform to use (e.g., 'openai'). Defaults to the server's configured default.")
    conversation_id: Optional[str] = Field(None, description="A unique identifier for the conversation session.")

    # --- Prompt Engineering & Customization ---
    system_prompt_override: Optional[str] = Field(None, description="A system prompt to override the default for this request.")
    persona: Optional[str] = Field(None, description="The name of a pre-defined persona to use as the system prompt.")

    # --- Advanced Features ---
    parameters: Optional[ModelParameters] = Field(None, description="Hyperparameters for the model.")
    json_mode: bool = Field(False, description="If True, instructs the model to return a valid JSON object.")

    # --- Template-based Prompting ---
    template: Optional[str] = Field(None, description="A prompt template with placeholders (e.g., 'Hello, {name}').")
    template_data: Optional[Dict[str, Any]] = Field(None, description="A dictionary of data to inject into the template.")

# --- Response Models ---

class ChatResponse(BaseModel):
    """The main response model for the /chat endpoint."""
    response: str = Field(..., description="The AI's generated response text.")
    conversation_id: Optional[str] = Field(None, description="The unique identifier for the conversation session.")

class StreamResponse(BaseModel):
    """The response model for the /chat/stream endpoint."""
    delta: str = Field(..., description="A chunk of the streaming response.")
    conversation_id: Optional[str] = Field(None, description="The unique identifier for the conversation session.")
