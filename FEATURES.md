### 1. Multi-Platform AI Integration
*   **Unified Interface:** A standardized `APIlatform` abstract base class ensures that regardless of the provider (OpenAI, Anthropic, Gemini, Groq), the request/response format remains consistent.
*   **Provider Support:**
    *   **Google Gemini:** Uses `google-genai` with support for system instructions and `gemini-1.5-flash`.
    *   **OpenAI:** Uses `AsyncOpenAI` with support for `gpt-4`.
    *   **Anthropic:** Uses `AsyncAnthropic` for Claude 3 Opus models.
    *   **Groq:** High-speed Llama3 integration via the `groq` SDK.
*   **JSON Mode:** Support for forcing LLMs to return valid JSON objects (supported in Gemini, OpenAI, and Groq implementations).

### 2. Intelligent Routing & Reliability
*   **Smart Fallback System:** If the primary requested platform fails, the gateway automatically cycles through a configured sequence (e.g., if OpenAI is down, it tries Anthropic, then Gemini).
*   **Circuit Breaker Pattern:** Uses `pybreaker` to track failure rates per platform. If a provider (like Anthropic) fails repeatedly, the circuit "opens," and subsequent requests skip that provider for a cooling period (60 seconds) to prevent cascading failures.
*   **Default Platform Configuration:** Centrally managed default platform and fallback order via environment variables.

### 3. Advanced Prompt Engineering
*   **Persona Library:** A dedicated directory (`src/personas/`) stores `.md` files (e.g., `helpful_programmer`, `sarcastic_assistant`). Users can trigger these by name in their API request.
*   **Dynamic Templates:** Supports Python-style string templates (e.g., `Hello, {name}`). The gateway renders these using `template_data` provided in the request before sending them to the AI.
*   **System Prompt Overrides:** Users can provide a `system_prompt_override` per request to bypass global settings.
*   **Global System Prompt:** A default system prompt (plaintext with emojis) is loaded from `system_prompts.md`.

### 4. Semantic Caching & Vector DB
*   **pgvector Integration:** Uses the `pgvector` extension in PostgreSQL to store and query high-dimensional vectors.
*   **Similarity Search:** Instead of exact-match caching, it uses `sentence-transformers` (`all-MiniLM-L6-v2`) to generate embeddings. It retrieves cached responses if a new prompt is semantically similar (default threshold 90%).
*   **Performance:** Reduces LLM API costs and latency for repetitive or similar queries.

### 5. Multi-Tenancy & Security
*   **Tiered Rate Limiting:** Redis-backed rate limiting with three tiers:
    *   **Free:** 5 requests / 60s.
    *   **Pro:** 100 requests / 60s.
    *   **Enterprise:** 1000 requests / 60s.
    *   **Unauthenticated:** 3 requests / 60s.
*   **Bring Your Own Key (BYOK):** Users can store their own API keys for OpenAI, Gemini, etc., in the database.
*   **Encryption at Rest:** User-provided API keys are encrypted using **Fernet (AES-128)** before being stored in PostgreSQL, with keys derived from the application's `SECRET_KEY`.
*   **API Key Authentication:** A custom Bearer token system where `APIKey` objects are linked to `User` accounts.

### 6. AI Guardrails (Input/Output Filtering)
The `GuardrailManager` scans every conversation against four specific security layers:
*   **Jailbreak Detection:** Regex patterns to catch "Ignore previous instructions" or "DAN" style attacks.
*   **Sensitive Data Detection:** Regex patterns to detect Credit Cards, SSNs, and Emails.
*   **SQL Injection Prevention:** Detects common SQL keywords (SELECT, DROP, UNION) in prompts.
*   **Unethical Request Blocking:** A keyword-based filter for illegal activities, hacking, or hate speech.
*   **Configurable Thresholds:** A `GUARDRAIL_BLOCK_THRESHOLD` determines how aggressive the blocking should be based on risk scores.

### 7. Observability & Analytics
*   **Usage Logging:** Every request logs prompt/completion tokens, latency (ms), and cost to the `usage_logs` table.
*   **Cost Calculation:** A utility maps token counts to real-world pricing for different models (e.g., GPT-4 vs. Gemini Flash) to provide USD estimates.
*   **Analytics API:** A `/analytics/report` endpoint provides:
    *   Usage summaries (total tokens/requests).
    *   Platform breakdown (which AI you use most).
    *   Cost trends over time.
    *   Latency trends (average response speed).
*   **Structured Logging:** Uses `structlog` to output machine-readable JSON logs.

### 8. Conversation Memory
*   **Persistent History:** All messages are stored in PostgreSQL linked to a `conversation_id`.
*   **Automatic Context Injection:** The `MemoryManager` automatically retrieves previous messages for a specific ID and prepends them to the new request, providing the AI with "short-term memory."

### 9. Privacy & Compliance
*   **PII Masking:** Integrates **Microsoft Presidio** to scan user prompts for Personally Identifiable Information (PII) and replaces it with `[REDACTED]` before sending the data to external AI providers (OpenAI/Google).

### 10. Streaming Support
*   **Real-time Response:** A `/chat/stream` endpoint using Server-Sent Events (SSE).
*   **Stream Caching:** Even streamed responses are captured in full and saved to the semantic cache once the stream completes.
*   **Token Estimation:** Since some providers don't return token counts for streams, a `tiktoken` utility provides fallback estimations.

### 11. Infrastructure & DevOps
*   **Dockerized:** Full `docker-compose.yml` including the FastAPI app, Redis (for throttling), and PostgreSQL with the `pgvector` image.
*   **Database Migrations:** Managed via `Alembic`, with versions for initial setup, BYOK updates, and semantic cache tables.
*   **Asynchronous Core:** Built entirely on `asyncio` using `AsyncSession` for database interactions and `httpx`-based AI SDKs to ensure high concurrency.