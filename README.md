# 🚀 FastAPI Multi-Platform AI Gateway

A production-ready, multi-platform AI gateway powered by FastAPI. This service integrates with **Google Gemini, OpenAI, Anthropic, and Groq** to provide a unified chat endpoint with custom system prompts, authentication, and rate limiting.

---

## 📂 Project Structure

```
fastapi-ai-endpoint/
├── README.md                  # Project documentation
├── pyproject.toml             # Project metadata & dependencies
├── requirements.txt           # Python dependencies
├── .python-version            # Python version (3.11)
└── src/
    ├── main.py                # FastAPI entrypoint
    ├── schema.py              # Request/Response models
    ├── config.py              # Configuration management
    │
    ├── ai/                    # AI-related logic
    │   ├── base.py            # Abstract AI platform interface
    │   ├── gemini.py          # Gemini implementation
    │   ├── openai.py          # OpenAI implementation
    │   ├── anthropic.py       # Anthropic implementation
    │   └── groq.py            # Groq implementation
    │
    ├── auth/                  # Authentication & Rate limiting
    │   ├── dependencies.py    # JWT-based auth handler
    │   └── throttling.py      # Request rate limiting logic
    │
    ├── prompts/               # Prompt management
    │   ├── prompt.py          # Loader for system prompts
    │   └── system_prompts.md  # Default system instructions
    │
    └── __init__.py (optional if needed)
```

---

## ⚡ Features

* ✅ **Unified Chat Endpoint** supporting **Google Gemini, OpenAI, Anthropic, and Groq**
* ✅ **System prompt customization** via `system_prompts.md`
* ✅ **JWT authentication** (optional)
* ✅ **Rate limiting** (different for authenticated vs unauthenticated users)
* ✅ **Swagger UI** for testing

---

## 🛠️ Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sidhyaashu/fastapi-ai-endpoint.git
cd fastapi-ai-endpoint
```

### 2️⃣ Create Virtual Environment (Python 3.11)

```bash
python3.11 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root. Add the API keys for the platforms you want to use.

```ini
# --- AI Platforms (at least one is required) ---
GOOGLE_API_KEY=your_google_genai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# --- Application Settings (optional) ---
# Set the default AI platform to use if not specified in the request
DEFAULT_PLATFORM=gemini

# Secret key for JWT authentication
SECRET_KEY=a-super-secret-key-at-least-256-bits-long
```

---

## 🚀 Run the Server

```bash
uvicorn src.main:app --reload
```

* API runs at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
* Interactive API Docs (Swagger UI): **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 📌 Endpoints

### **1. Root Check**

```http
GET /
```

Response:

```json
{"message": "API is Running...!!"}
```

---

### **2. Chat Endpoint**

```http
POST /chat
Content-Type: application/json
Authorization: Bearer <your_jwt_token>   # Optional
```

#### Request:

The `platform` field is optional. If omitted, the `DEFAULT_PLATFORM` from your `.env` file will be used.

```json
{
  "prompt": "Hello, how are you?",
  "platform": "openai"
}
```

#### Response:

```json
{
  "response": "Hi there! I'm doing great 😃 How about you?"
}
```

---

## 🔐 Authentication & Rate Limiting

* **Without token** → treated as `global_unauthenticated_user`

  * Limit: **3 requests / 60 sec**
* **With valid JWT token**

  * Limit: **5 requests / 60 sec**
* If exceeded:

```json
{
  "detail": "Too many requests. Please try again later."
}
```

---

## 🧠 AI Platforms

The service supports multiple AI models. The default models are:

*   **Gemini**: `gemini-1.5-flash`
*   **OpenAI**: `gpt-4`
*   **Anthropic**: `claude-3-opus-20240229`
*   **Groq**: `llama3-8b-8192`

* **System Prompt** (`src/prompts/system_prompts.md`):

```
Answer the user in plaintext (no markdown), but use emojis! Be simple, clear and concise
```

This ensures **emoji-friendly**, **plain text**, **concise responses** across all platforms.

---

## 🧪 Testing

### Using `curl`

To use the default platform:
```bash
curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{"prompt": "Tell me a joke"}'
```

To specify a platform (e.g., `groq`):
```bash
curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{"prompt": "Tell me a joke", "platform": "groq"}'
```

### Using Swagger UI

Visit **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** and test interactively.

---

## 📖 Future Improvements

* Add **JWT token generation endpoint**
* Add **logging & monitoring**
* Add **Docker support** for deployment

---

## 👨‍💻 Author

Built with ❤️ by [Asutosh Sidhya](https://github.com/sidhyaashu)
