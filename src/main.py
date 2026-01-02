from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from functools import lru_cache
import time
from typing import List, Optional
from sqlalchemy.orm import Session
import pybreaker

from src import config
from src.ai.base import APIlatform
from src.ai.gemini import Gemini
from src.ai.openai import OpenAI
from src.ai.anthropic import Anthropic
from src.ai.groq import Groq
from src.auth.dependencies import get_user_identifier
from src.auth.throttling import apply_rate_limit
from src.database.models import User, UsageLog
from src.prompts.prompt import load_system_prompt
from src.prompts.persona import get_persona_prompt
from src.prompts.template import render_template
from src.schema import ChatRequest, ChatResponse, Message, StreamResponse, TokenUsage
from src.memory.manager import MemoryManager, get_memory_manager
from src.cache.manager import cache_manager
from src.security.pii_masking import mask_pii_in_messages
from src.utils.logger import logger
from src.utils.cost_calculator import calculate_cost
from src.utils.circuit_breaker import get_breaker
from src.utils.token_counter import count_tokens
from src.database.session import get_db, SessionLocal
import redis

app = FastAPI(title="AI endpoint Using FastAPI")

def get_current_user(user_id: str = Depends(get_user_identifier), db: Session = Depends(get_db)) -> User | None:
    if user_id == "global_unauthenticated_user":
        return None
    return db.query(User).filter(User.id == user_id).first()

class PlatformProvider:
    def __init__(self, user: User | None = None):
        self.platforms = {}
        self.system_prompt = load_system_prompt()
        self.user = user

    def register_platform(self, name: str, platform_class, api_key: str, model_name: str):
        user_byok = self.user.get_byok(name) if self.user else None
        final_api_key = user_byok or api_key

        if final_api_key:
            self.platforms[name] = platform_class(
                api_key=final_api_key,
                model_name=model_name,
                system_prompt=self.system_prompt,
            )
            logger.info("Registered AI platform", platform=name, user_id=self.user.id if self.user else "system")

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

def get_platform_provider(user: User | None = Depends(get_current_user)):
    provider = PlatformProvider(user)
    provider.register_platform("gemini", Gemini, config.GEMINI_API_KEY, config.GEMINI_MODEL_NAME)
    provider.register_platform("openai", OpenAI, config.OPENAI_API_KEY, config.OPENAI_MODEL_NAME)
    provider.register_platform("anthropic", Anthropic, config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL_NAME)
    provider.register_platform("groq", Groq, config.GROQ_API_KEY, config.GROQ_MODEL_NAME)
    return provider

def log_usage(user_id: str, platform: str, token_usage: TokenUsage, latency_ms: float, model_name: str):
    db = SessionLocal()
    try:
        cost = calculate_cost(model_name, token_usage)
        log_entry = UsageLog(
            user_id=user_id,
            platform=platform,
            prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens,
            total_tokens=token_usage.total_tokens,
            latency_ms=latency_ms,
            cost=cost,
        )
        db.add(log_entry)
        db.commit()
    finally:
        db.close()

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

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise HTTPException(status_code=503, detail="Database connection failed.")
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
    background_tasks: BackgroundTasks,
    user: User | None = Depends(get_current_user),
    provider: PlatformProvider = Depends(get_platform_provider),
    memory_manager: MemoryManager = Depends(get_memory_manager),
):
    apply_rate_limit(user)

    user_id = user.id if user else "global_unauthenticated_user"
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
    start_time = time.time()
    for ai_platform in platform_sequence:
        platform_name = ai_platform.__class__.__name__.lower()
        breaker = get_breaker(platform_name)
        try:
            logger.info("Attempting AI platform", platform=platform_name)
            response_text, token_usage = await breaker.call_async(
                ai_platform.chat,
                messages=masked_conversation,
                parameters=request.parameters,
                system_prompt=system_prompt,
                json_mode=request.json_mode,
            )
            latency_ms = (time.time() - start_time) * 1000

            assistant_message = Message(role="assistant", content=response_text)
            memory_manager.add_message(conversation_id, assistant_message, user_id)
            cache_manager.set(full_conversation, response_text)

            if user:
                background_tasks.add_task(log_usage, user.id, platform_name, token_usage, latency_ms, ai_platform.model_name)

            logger.info("AI call successful", platform=platform_name, conversation_id=conversation_id)
            return ChatResponse(response=response_text, conversation_id=conversation_id, token_usage=token_usage)
        except pybreaker.CircuitBreakerError as e:
            last_error = e
            logger.warn("Circuit breaker open for platform", platform=platform_name, error=str(e))
            continue
        except Exception as e:
            last_error = e
            logger.error("AI platform failed", platform=ai_platform.__class__.__name__, error=str(e))
            continue

    logger.error("All AI platforms failed", last_error=str(last_error))
    raise HTTPException(status_code=500, detail=f"All AI platforms failed. Last error: {last_error}")

async def stream_generator(stream, conversation_id: str, original_conversation: List[Message], memory_manager: MemoryManager, user_id: str, platform: str, model_name: str, start_time: float, background_tasks: BackgroundTasks):
    full_response = ""
    async for chunk in stream:
        full_response += chunk
        yield f"data: {StreamResponse(delta=chunk, conversation_id=conversation_id).model_dump_json()}\n\n"

    latency_ms = (time.time() - start_time) * 1000
    assistant_message = Message(role="assistant", content=full_response)
    memory_manager.add_message(conversation_id, assistant_message, user_id)
    cache_manager.set(original_conversation, full_response)

    if user_id != "global_unauthenticated_user":
        prompt_tokens = count_tokens(original_conversation, model_name)
        completion_tokens = count_tokens([assistant_message], model_name)
        token_usage = TokenUsage(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens)
        background_tasks.add_task(log_usage, user_id, platform, token_usage, latency_ms, model_name)

    logger.info("Streaming response completed", conversation_id=conversation_id, platform=platform)

@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User | None = Depends(get_current_user),
    provider: PlatformProvider = Depends(get_platform_provider),
    memory_manager: MemoryManager = Depends(get_memory_manager),
):
    apply_rate_limit(user)

    user_id = user.id if user else "global_unauthenticated_user"
    conversation_id, full_conversation = _process_request(request, memory_manager, user_id)

    cached_response = cache_manager.get(full_conversation)
    if cached_response:
        logger.info("Cache hit for streaming", conversation_id=conversation_id)
        async def single_chunk_stream():
            yield f"data: {StreamResponse(delta=cached_response, conversation_id=conversation_id).model_dump_json()}\n\n"
        return StreamingResponse(single_chunk_stream(), media_type="text/event-stream")

    system_prompt = _get_system_prompt(request)
    platform_sequence = provider.get_platform_sequence(request.platform)
    masked_conversation = mask_pii_in_messages(full_conversation)

    async def try_platforms_stream():
        last_error = None
        start_time = time.time()
        for ai_platform in platform_sequence:
            platform_name = ai_platform.__class__.__name__.lower()
            breaker = get_breaker(platform_name)
            try:
                logger.info("Attempting AI platform for streaming", platform=platform_name)
                stream = await breaker.call_async(
                    ai_platform.stream_chat,
                    messages=masked_conversation,
                    parameters=request.parameters,
                    system_prompt=system_prompt,
                    json_mode=request.json_mode,
                )
                return stream_generator(stream, conversation_id, full_conversation, memory_manager, user_id, platform_name, ai_platform.model_name, start_time, background_tasks)
            except pybreaker.CircuitBreakerError as e:
                last_error = e
                logger.warn("Circuit breaker open for streaming", platform=platform_name, error=str(e))
                continue
            except Exception as e:
                last_error = e
                logger.error("AI platform failed for streaming", platform=ai_platform.__class__.__name__, error=str(e))
                continue
        logger.error("All AI platforms failed for streaming", last_error=str(last_error))

    return StreamingResponse(try_platforms_stream(), media_type="text/event-stream")
