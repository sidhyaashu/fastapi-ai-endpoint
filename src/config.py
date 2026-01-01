import os
from dotenv import load_dotenv

load_dotenv()

# AI Platforms
DEFAULT_PLATFORM = os.getenv("DEFAULT_PLATFORM", "gemini")

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


# Rate Limiting
GLOBAL_RATE_LIMIT = 3
GLOBAL_TIME_WINDOW_SECONDS = 60
AUTH_RATE_LIMIT = 5
AUTH_TIME_WINDOW_SECONDS = 60

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "a-string-secret-at-least-256-bits-long")
ALGORITHM = "HS256"
