# 🚀 FastAPI Advanced AI Gateway

An enterprise-ready, multi-platform AI gateway powered by FastAPI. This service integrates with **Google Gemini, OpenAI, Anthropic, and Groq** and includes a rich feature set for reliability, security, and advanced prompt engineering.

---

## 📂 Project Structure

The project is organized into modules for AI, authentication, caching, memory, prompts, and security, ensuring a clean and maintainable codebase.

---

## ⚡ Core Features

*   ✅ **Multi-Platform Support**: Unified API for Google Gemini, OpenAI, Anthropic, and Groq.
*   ✅ **Streaming Responses**: Real-time, token-by-token streaming via a `/chat/stream` endpoint.
*   ✅ **Conversation Memory**: Maintains conversation history using a unique `conversation_id`.
*   ✅ **Smart Fallback**: Automatically retries requests with other platforms if a provider fails.

## ✨ Advanced Features

*   ✅ **Semantic Caching**: Reduces latency and cost by caching identical requests.
*   ✅ **PII Masking**: Automatically redacts sensitive information (e.g., emails) before sending to AI providers.
*   ✅ **Dynamic Prompt Templates**: Inject variables into your prompts for dynamic content generation.
*   ✅ **Persona Library**: Switch between pre-defined system prompts (personas) on the fly.
*   ✅ **System Prompt Override**: Customize the system prompt for a single request.
*   ✅ **JSON Mode**: Enforce structured JSON output from compatible models.
*   ✅ **Hyperparameter Control**: Adjust `temperature` and `max_tokens` for fine-tuned responses.

---

## 🛠️ Setup

### 1️⃣ Clone the Repository & Install Dependencies

```bash
git clone https://github.com/sidhyaashu/fastapi-ai-endpoint.git
cd fastapi-ai-endpoint
# Create a virtual environment (Python 3.11)
python3.11 -m venv venv && source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configure Environment Variables

Create a `.env` file in the project root. Add API keys for the platforms you want to use and configure the application settings.

```ini
# --- AI Platforms (at least one is required) ---
GOOGLE_API_KEY=your_google_genai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# --- Application Settings ---
# The default platform to use if not specified in the request.
DEFAULT_PLATFORM=gemini

# A comma-separated list of platforms to use as fallbacks, in order.
FALLBACK_PLATFORMS=openai,anthropic

# Secret key for JWT authentication.
SECRET_KEY=a-super-secret-key-at-least-256-bits-long
```

---

## 🚀 Run the Server

```bash
uvicorn src.main:app --reload
```

*   **API URL**: `http://127.0.0.1:8000`
*   **Swagger UI (Interactive Docs)**: `http://127.0.0.1:8000/docs`

---

## 📌 API Endpoints & Usage

### **1. Standard Chat: `/chat`**

This endpoint sends a request and waits for the full response to be generated.

#### Full Request Example:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of {country}?"
    }
  ],
  "platform": "openai",
  "conversation_id": "conv-12345",
  "system_prompt_override": "You are a helpful geography expert.",
  "persona": "helpful_programmer",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 100
  },
  "json_mode": false,
  "template": "What is the capital of {country}?",
  "template_data": {
    "country": "France"
  }
}
```

### **2. Streaming Chat: `/chat/stream`**

This endpoint streams the response token by token as Server-Sent Events (SSE).

#### Example `curl` for Streaming:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
-H "Content-Type: application/json" \
-d '{
  "messages": [{"role": "user", "content": "Write a short story about a robot."}],
  "platform": "groq"
}'
```

---

## 👨‍💻 Author

Built with ❤️ by [Asutosh Sidhya](https://github.com/sidhyaashu)
