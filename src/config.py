import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

# --- Database and Cache Configuration ---
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/mydatabase")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


# --- AI Platform Configuration ---

# The default platform to use when none is specified in the request.
DEFAULT_PLATFORM = os.getenv("DEFAULT_PLATFORM", "gemini")

# A comma-separated list of platforms to try in order if the primary one fails.
# Example: FALLBACK_PLATFORMS=openai,anthropic,gemini
FALLBACK_PLATFORMS_STR = os.getenv("FALLBACK_PLATFORMS", "openai,gemini")
FALLBACK_PLATFORMS: List[str] = [p.strip() for p in FALLBACK_PLATFORMS_STR.split(",") if p.strip()]


# --- API Keys and Model Names ---

# Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-4"

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = "claude-3-opus-20240229"

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = "llama3-8b-8192"


# --- Rate Limiting ---
GLOBAL_RATE_LIMIT = 3
GLOBAL_TIME_WINDOW_SECONDS = 60
AUTH_RATE_LIMIT = 5
AUTH_TIME_WINDOW_SECONDS = 60

# --- JWT Authentication ---
SECRET_KEY = os.getenv("SECRET_KEY", "a-string-secret-at-least-256-bits-long")
ALGORITHM = "HS256"

# --- Security and Guardrails ---
GUARDRAIL_BLOCK_THRESHOLD = float(os.getenv("GUARDRAIL_BLOCK_THRESHOLD", 0.85))
