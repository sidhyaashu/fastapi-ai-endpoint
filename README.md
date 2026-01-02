# 🚀 FastAPI Enterprise AI Gateway

An enterprise-ready, multi-platform AI gateway powered by FastAPI. This service integrates with **Google Gemini, OpenAI, Anthropic, and Groq** and includes a rich feature set for reliability, security, and advanced prompt engineering, all backed by a persistent PostgreSQL and Redis infrastructure.

---

## 📂 Project Structure

The project is organized into modules for AI, authentication, caching, memory, prompts, security, and utils, ensuring a clean and maintainable codebase.

---

## ⚡ Core Features

*   ✅ **Multi-Platform Support**: Unified API for Google Gemini, OpenAI, Anthropic, and Groq.
*   ✅ **Streaming Responses**: Real-time, token-by-token streaming via a `/chat/stream` endpoint.
*   ✅ **Persistent Conversation Memory**: Maintains conversation history in a PostgreSQL database.
*   ✅ **Smart Fallback & Circuit Breaker**: Automatically retries requests with other platforms and temporarily disables failing providers.

## ✨ Advanced Features

*   ✅ **Multi-Tenancy**: Supports different user tiers with varying rate limits.
*   ✅ **Bring Your Own Key (BYOK)**: Allows users to provide their own encrypted API keys.
*   ✅ **Observability & Billing Foundation**: Logs usage data (tokens, latency, cost) to a PostgreSQL database.
*   ✅ **Redis Caching**: Reduces latency and cost by caching identical requests in Redis with a TTL.
*   ✅ **Scalable Rate Limiting**: Enforces rate limits across multiple instances using Redis.
*   ✅ **Robust PII Masking**: Automatically redacts a wide range of sensitive information using Microsoft Presidio.
*   ✅ **Token Counting**: Tracks and returns token usage for each request, essential for billing and analytics.
*   ✅ **Dynamic Prompt Templates**: Inject variables into your prompts for dynamic content generation.
*   ✅ **Persona Library**: Switch between pre-defined system prompts (personas) on the fly.
*   ✅ **Containerized Deployment**: Includes a `Dockerfile` and `docker-compose.yml` for a one-command setup.

---

## 🛠️ Setup

### 1️⃣ Prerequisites

*   **Docker** and **Docker Compose**
*   **Python 3.11**

### 2️⃣ Clone the Repository & Install Dependencies

```bash
git clone https://github.com/sidhyaashu/fastapi-ai-endpoint.git
cd fastapi-ai-endpoint
# Create a virtual environment
python3.11 -m venv venv && source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```ini
# --- Infrastructure ---
DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
REDIS_URL=redis://localhost:6379

# --- AI Platforms (at least one is required) ---
GOOGLE_API_KEY=your_google_genai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# --- Application Settings ---
DEFAULT_PLATFORM=gemini
FALLBACK_PLATFORMS=openai,anthropic
SECRET_KEY=a-super-secret-key-at-least-256-bits-long
```

### 4️⃣ Run Infrastructure & Server

1.  **Start PostgreSQL and Redis**:
    ```bash
    docker-compose up -d
    ```
2.  **Run the FastAPI Server**:
    ```bash
    uvicorn src.main:app --reload
    ```

*   **API URL**: `http://127.0.0.1:8000`
*   **Swagger UI**: `http://127.0.0.1:8000/docs`

---

## 📌 API Endpoints & Usage

The API is now fully containerized. You can also run the application with:
```bash
docker-compose up --build
```
This will build the FastAPI application image, start the PostgreSQL and Redis containers, and run the application.

---

## 👨‍💻 Author

Built with ❤️ by [Asutosh Sidhya](https://github.com/sidhyaashu)
