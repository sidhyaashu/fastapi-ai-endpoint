import os
from dotenv import load_dotenv

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# Rate Limiting
GLOBAL_RATE_LIMIT = 3
GLOBAL_TIME_WINDOW_SECONDS = 60
AUTH_RATE_LIMIT = 5
AUTH_TIME_WINDOW_SECONDS = 60

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "a-string-secret-at-least-256-bits-long")
ALGORITHM = "HS256"
