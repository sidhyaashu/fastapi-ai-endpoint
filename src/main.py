import os 
from fastapi import FastAPI, Depends, HTTPException
from src.schema import ChatRequest, ChatResponse
from src.prompts.prompt import load_system_prompt
from dotenv import load_dotenv
from src.ai.base import APIlatform
from src.ai.gemini import Gemini
from src.auth.throttling import apply_rate_limit
from src.auth.dependencies import get_user_identifier

load_dotenv()


app = FastAPI(title="AI endpoint Using FastAPI")

from src import config

def get_ai_platform():
    system_prompt = load_system_prompt()

    if not config.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key is not set.")

    return Gemini(api_key=config.GEMINI_API_KEY, model_name=config.GEMINI_MODEL_NAME, system_prompt=system_prompt)


@app.get('/')
async def root():
    return {"message":"API is Running...!!"}

@app.post('/chat',response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(get_user_identifier), ai_platform: APIlatform = Depends(get_ai_platform)):
    apply_rate_limit(user_id)
    response_test = await ai_platform.chat(request.prompt)
    return ChatResponse(response=response_test)
