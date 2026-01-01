from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from functools import lru_cache
import asyncio
from typing import List, Optional

from src import config
from src.ai.base import APIlatform
from src.ai.gemini import Gemini
from src.ai.openai import OpenAI
from src.ai.anthropic import Anthropic
from src.ai.groq import Groq
from src.auth.dependencies import get_user_identifier
from src.auth.throttling import apply_rate_limit
from src.prompts.prompt import load_system_prompt
from src.prompts.persona import get_persona_prompt
from src.prompts.template import render_template
from src.schema import ChatRequest, ChatResponse, Message, StreamResponse
from src.memory.manager import MemoryManager, get_memory_manager
from src.cache.manager import cache_manager
from src.security.pii_masking import mask_pii_in_messages
from src.utils.logger import logger
from src.database.session import get_db
import redis

app = FastAPI(title="AI endpoint Using FastAPI")

class PlatformProvider:
    def __init__(self):
        self.platforms = {}
        self.system_prompt = load_system_prompt()

    def register_platform(self, name: str, platform_class, api_key: str, model_name: str):
        if api_key:
            self.platforms[name] = platform_class(
                api_key=api_key,
                model_name=model_name,
                system_prompt=self.system_prompt,
            )
            logger.info("Registered AI platform", platform=name)

    def get_platform(self, name: str) -> Optional[APIlatform]:
        return self.platforms.get(name)

    def get_platform_sequence(self, requested_platform: Optional[str]) -> List[APIlatform]:
        sequence = []
        if requested_platform and (platform := self.get_platform(requested_platform)):
            if platform not in sequence:
                sequence.append(platform)
        if (default_platform := self.get_platform(config.DEFAULT_PLATFORM)):
            if default_platform not in sequence:
                sequence.append(default_platform)
        for fallback_name in config.FALLBACK_PLATFORMS:
            if (fallback_platform := self.get_platform(fallback_name)):
                if fallback_platform not in sequence:
                    sequence.append(fallback_platform)
        if not sequence:
            raise HTTPException(status_code=503, detail="No AI platforms are available.")
        return sequence

@lru_cache(maxsize=1)
def get_platform_provider():
    provider = PlatformProvider()
    provider.register_platform("gemini", Gemini, config.GEMINI_API_KEY, config.GEMINI_MODEL_NAME)
    provider.register_platform("openai", OpenAI, config.OPENAI_API_KEY, config.OPENAI_MODEL_NAME)
    provider.register_platform("anthropic", Anthropic, config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL_NAME)
    provider.register_platform("groq", Groq, config.GROQ_API_KEY, config.GROQ_MODEL_NAME)
    return provider


def _process_request(request: ChatRequest, memory_manager: MemoryManager, user_id: str):
    conversation_id = request.conversation_id or memory_manager.generate_conversation_id()
    history = memory_manager.get_history(conversation_id)
    if request.template and request.template_data:
        last_message_content = render_template(request.template, request.template_data)
        if not last_message_content:
            raise HTTPException(status_code=400, detail="Failed to render the provided template.")
        request.messages[-1].content = last_message_content
    for message in request.messages:
        memory_manager.add_message(conversation_id, message, user_id)
    full_conversation = history + request.messages
    return conversation_id, full_conversation

def _get_system_prompt(request: ChatRequest) -> str:
    if request.system_prompt_override:
        return request.system_prompt_override
    if request.persona:
        persona_prompt = get_persona_prompt(request.persona)
        if not persona_prompt:
            raise HTTPException(status_code=400, detail=f"Persona '{request.persona}' not found.")
        return persona_prompt
    return None


@app.get("/")
async def root():
    return {"message": "API is Running...!!"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    # Check DB connection
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise HTTPException(status_code=503, detail="Database connection failed.")

    # Check Redis connection
    try:
        redis_client = redis.from_url(config.REDIS_URL)
        redis_client.ping()
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        raise HTTPException(status_code=503, detail="Redis connection failed.")

    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_user_identifier),
    provider: PlatformProvider = Depends(get_platform_provider),
    memory_manager: MemoryManager = Depends(get_memory_manager),
):
    apply_rate_limit(user_id)

    conversation_id, full_conversation = _process_request(request, memory_manager, user_id)

    cached_response = cache_manager.get(full_conversation)
    if cached_response:
        logger.info("Cache hit", conversation_id=conversation_id)
        return ChatResponse(response=cached_response, conversation_id=conversation_id)
    logger.info("Cache miss", conversation_id=conversation_id)

    system_prompt = _get_system_prompt(request)
    platform_sequence = provider.get_platform_sequence(request.platform)

    masked_conversation = mask_pii_in_messages(full_conversation)

    last_error = None
    for ai_platform in platform_sequence:
        try:
            platform_name = ai_platform.__class__.__name__
            logger.info("Attempting AI platform", platform=platform_name)
            response_text, token_usage = await ai_platform.chat(
                messages=masked_conversation,
                parameters=request.parameters,
                system_prompt=system_prompt,
                json_mode=request.json_mode,
            )

            assistant_message = Message(role="assistant", content=response_text)
            memory_manager.add_message(conversation_id, assistant_message, user_id)
            cache_manager.set(full_conversation, response_text)

            logger.info("AI call successful", platform=platform_name, conversation_id=conversation_id)
            return ChatResponse(response=response_text, conversation_id=conversation_id, token_usage=token_usage)
        except Exception as e:
            last_error = e
            logger.error("AI platform failed", platform=ai_platform.__class__.__name__, error=str(e))
            continue

    logger.error("All AI platforms failed", last_error=str(last_error))
    raise HTTPException(status_code=500, detail=f"All AI platforms failed. Last error: {last_error}")


async def stream_generator(stream, conversation_id: str, original_conversation: List[Message], memory_manager: MemoryManager, user_id: str):
    full_response = ""
    async for chunk in stream:
        full_response += chunk
        response_data = StreamResponse(delta=chunk, conversation_id=conversation_id)
        yield f"data: {response_data.model_dump_json()}\n\n"

    assistant_message = Message(role="assistant", content=full_response)
    memory_manager.add_message(conversation_id, assistant_message, user_id)
    cache_manager.set(original_conversation, full_response)
    logger.info("Streaming response completed and cached", conversation_id=conversation_id)

@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: str = Depends(get_user_identifier),
    provider: PlatformProvider = Depends(get_platform_provider),
    memory_manager: MemoryManager = Depends(get_memory_manager),
):
    apply_rate_limit(user_id)

    conversation_id, full_conversation = _process_request(request, memory_manager, user_id)

    cached_response = cache_manager.get(full_conversation)
    if cached_response:
        logger.info("Cache hit for streaming", conversation_id=conversation_id)
        async def single_chunk_stream():
            response_data = StreamResponse(delta=cached_response, conversation_id=conversation_id)
            yield f"data: {response_data.model_dump_json()}\n\n"
        return StreamingResponse(single_chunk_stream(), media_type="text/event-stream")
    logger.info("Cache miss for streaming", conversation_id=conversation_id)

    system_prompt = _get_system_prompt(request)
    platform_sequence = provider.get_platform_sequence(request.platform)
    masked_conversation = mask_pii_in_messages(full_conversation)

    async def try_platforms_stream():
        last_error = None
        for ai_platform in platform_sequence:
            try:
                platform_name = ai_platform.__class__.__name__
                logger.info("Attempting AI platform for streaming", platform=platform_name)
                stream = ai_platform.stream_chat(
                    messages=masked_conversation,
                    parameters=request.parameters,
                    system_prompt=system_prompt,
                    json_mode=request.json_mode,
                )
                return stream_generator(stream, conversation_id, full_conversation, memory_manager, user_id)
            except Exception as e:
                last_error = e
                logger.error("AI platform failed for streaming", platform=ai_platform.__class__.__name__, error=str(e))
                continue
        logger.error("All AI platforms failed for streaming", last_error=str(last_error))

    final_stream_generator = try_platforms_stream()

    return StreamingResponse(
        final_stream_generator,
        media_type="text/event-stream"
    )
