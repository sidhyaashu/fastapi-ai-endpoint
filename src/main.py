from fastapi import FastAPI, Depends, HTTPException
from functools import lru_cache

from src import config
from src.ai.base import APIlatform
from src.ai.gemini import Gemini
from src.ai.openai import OpenAI
from src.ai.anthropic import Anthropic
from src.ai.groq import Groq
from src.auth.dependencies import get_user_identifier
from src.auth.throttling import apply_rate_limit
from src.prompts.prompt import load_system_prompt
from src.schema import ChatRequest, ChatResponse


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

    def get_platform(self, name: str) -> APIlatform:
        platform = self.platforms.get(name)
        if not platform:
            raise HTTPException(status_code=400, detail=f"Platform '{name}' is not available.")
        return platform

@lru_cache(maxsize=1)
def get_platform_provider():
    provider = PlatformProvider()
    provider.register_platform("gemini", Gemini, config.GEMINI_API_KEY, config.GEMINI_MODEL_NAME)
    provider.register_platform("openai", OpenAI, config.OPENAI_API_KEY, config.OPENAI_MODEL_NAME)
    provider.register_platform("anthropic", Anthropic, config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL_NAME)
    provider.register_platform("groq", Groq, config.GROQ_API_KEY, config.GROQ_MODEL_NAME)
    return provider


@app.get("/")
async def root():
    return {"message": "API is Running...!!"}


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_user_identifier),
    provider: PlatformProvider = Depends(get_platform_provider),
):
    apply_rate_limit(user_id)
    platform_name = request.platform or config.DEFAULT_PLATFORM
    ai_platform = provider.get_platform(platform_name)
    response_text = await ai_platform.chat(request.prompt)
    return ChatResponse(response=response_text)
