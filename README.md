
# 🚀 FastAPI AI Endpoint

A production-ready **AI-powered FastAPI service** that integrates with **Google Gemini** to provide chat responses with custom system prompts, authentication, and rate limiting.

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
    ├── constant.py            # Rate limits & auth constants
    │
    ├── ai/                    # AI-related logic
    │   ├── base.py            # Abstract AI platform interface
    │   └── gemini.py          # Gemini implementation
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

* ✅ **AI Chat Endpoint** using **Google Gemini**
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

Create a `.env` file in the project root:

```ini
GOOGLE_API_KEY=your_google_genai_api_key_here
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

```json
{
  "prompt": "Hello, how are you?"
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

## 🧠 AI Model

* Backend uses **Google Gemini** via `google-genai`
* Default Model: `gemini-2.0-flash`
* **System Prompt** (`src/prompts/system_prompts.md`):

```
Answer the user in plaintext (no markdown), but use emojis! Be simple, clear and concise
```

This ensures **emoji-friendly**, **plain text**, **concise responses**.

---

## 🧪 Testing

### Using `curl`

```bash
curl -X POST http://127.0.0.1:8000/chat \
-H "Content-Type: application/json" \
-d '{"prompt": "Tell me a joke"}'
```

### Using Swagger UI

Visit **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** and test interactively.

---

## 📖 Future Improvements

* Add **JWT token generation endpoint**
* Support for **multiple AI models** (OpenAI, Anthropic, etc.)
* Add **logging & monitoring**
* Add **Docker support** for deployment

---

## 👨‍💻 Author

Built with ❤️ by [Asutosh Sidhya](https://github.com/sidhyaashu)