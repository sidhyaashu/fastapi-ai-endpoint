import os 
from fastapi import FastAPI, Depends
from src.schema import ChatRequest, ChatResponse
from src.prompts.prompt import load_system_prompt
from dotenv import load_dotenv
from src.ai.gemini import Gemini
from src.auth.throttling import apply_rate_limit
from src.auth.dependencies import get_user_identifier

load_dotenv()


app = FastAPI(title="AI endpoint Using FastAPI")

system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

ai_platform = Gemini(api_key=gemini_api_key,model_name="gemini-2.0-flash",system_prompt=system_prompt)


@app.get('/')
async def root():
    return {"message":"API is Running...!!"}

@app.post('/chat',response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(get_user_identifier)):
    apply_rate_limit(user_id)
    response_test = ai_platform.chat(request.prompt)
    return ChatResponse(response=response_test)