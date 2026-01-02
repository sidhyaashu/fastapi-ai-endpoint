# 🚀 FastAPI Enterprise AI Gateway

An enterprise-ready, multi-platform AI gateway powered by FastAPI. This service integrates with **Google Gemini, OpenAI, Anthropic, and Groq** and includes a rich feature set for reliability, security, and advanced prompt engineering, all backed by a persistent PostgreSQL and Redis infrastructure.

---

## 📂 Project Structure

The project is organized into modules for AI, authentication, caching, memory, prompts, security, guardrails, analytics, and utils, ensuring a clean and maintainable codebase.

---

## ⚡ Core Features

*   ✅ **Multi-Platform Support**: Unified API for Google Gemini, OpenAI, Anthropic, and Groq.
*   ✅ **Streaming Responses**: Real-time, token-by-token streaming via a `/chat/stream` endpoint.
*   ✅ **Persistent Conversation Memory**: Maintains conversation history in a PostgreSQL database.
*   ✅ **Smart Fallback & Circuit Breaker**: Automatically retries requests with other platforms and temporarily disables failing providers.
*   ✅ **Semantic Caching**: Reduces latency and cost by caching responses to semantically similar requests using `pgvector` and sentence transformers.

## ✨ Advanced Features

*   ✅ **Multi-Tenancy**: Supports different user tiers with varying rate limits.
*   ✅ **Bring Your Own Key (BYOK)**: Allows users to provide their own encrypted API keys.
*   ✅ **User-Facing Analytics API**: Provides a `/analytics/report` endpoint for users to track their usage, costs, and latency.
*   ✅ **Observability & Billing Foundation**: Logs usage data (tokens, latency, cost) to a PostgreSQL database.
*   ✅ **Scalable Rate Limiting**: Enforces rate limits across multiple instances using Redis.
*   ✅ **Robust PII Masking**: Automatically redacts a wide range of sensitive information using Microsoft Presidio.
*   ✅ **Token Counting**: Tracks and returns token usage for each request, essential for billing and analytics.
*   ✅ **Dynamic Prompt Templates**: Inject variables into your prompts for dynamic content generation.
*   ✅ **Persona Library**: Switch between pre-defined system prompts (personas) on the fly.
*   ✅ **Containerized Deployment**: Includes a `Dockerfile` and `docker-compose.yml` for a one-command setup.

## 🛡️ Security

*   ✅ **AI Guardrails**: A configurable system to scan and block malicious or harmful user prompts.
    *   **Sensitive Data Detection**: Blocks requests containing potential PII.
    *   **SQL Injection Prevention**: Detects and blocks common SQL injection patterns.
    *   **Unethical Request Blocking**: Flags requests related to illegal or unethical activities.
    *   **Jailbreak Attempt Prevention**: Identifies and blocks common prompt injection techniques.

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
# For the FastAPI application (async driver)
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mydatabase
# For Alembic migrations (sync driver)
SYNC_DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
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

# --- Security & Guardrails ---
GUARDRAIL_BLOCK_THRESHOLD=0.85
```

### 4️⃣ Run Infrastructure & Server

1.  **Start PostgreSQL and Redis**:
    ```bash
    docker-compose up -d postgres redis
    ```
2.  **Apply Database Migrations**:
    ```bash
    alembic upgrade head
    ```
3.  **Run the FastAPI Server**:
    *   **For local development**:
        ```bash
        uvicorn src.main:app --reload
        ```
    *   **For production (using Docker)**:
        ```bash
        docker-compose up --build app
        ```

*   **API URL**: `http://127.0.0.1:8000`
*   **Swagger UI**: `http://127.0.0.1:8000/docs`

---

## 📌 API Endpoints & Usage

The API includes endpoints for chat, streaming chat, and analytics. All endpoints are documented in the Swagger UI.

*   `/chat`: Standard request-response chat.
*   `/chat/stream`: Server-sent events for real-time streaming.
*   `/analytics/report`: Get a usage and cost report for your user. (Requires authentication)

---

## 👨‍💻 Author

Built with ❤️ by [Asutosh Sidhya](https://github.com/sidhyaashu)
