import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from src.database.models import User, APIKey

pytestmark = pytest.mark.asyncio

@respx.mock
async def test_chat_endpoint_success(client: TestClient, test_user: User, test_api_key: APIKey):
    respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent").mock(
        return_value=Response(200, json={"candidates": [{"content": {"parts": [{"text": "Mocked response"}]}}]})
    )

    headers = {"Authorization": "Bearer test_key"}
    payload = {"messages": [{"role": "user", "content": "Hello"}]}

    response = client.post("/chat", headers=headers, json=payload)

    assert response.status_code == 200
    assert response.json()["response"] == "Mocked response"

@respx.mock
async def test_chat_fallback_logic(client: TestClient, test_user: User, test_api_key: APIKey):
    respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent").mock(
        return_value=Response(500)
    )
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(200, json={"choices": [{"message": {"content": "OpenAI fallback response"}}]})
    )

    headers = {"Authorization": "Bearer test_key"}
    payload = {"messages": [{"role": "user", "content": "Hello"}]}

    response = client.post("/chat", headers=headers, json=payload)

    assert response.status_code == 200
    assert response.json()["response"] == "OpenAI fallback response"

async def test_max_tokens_validation(client: TestClient, test_user: User, test_api_key: APIKey):
    headers = {"Authorization": "Bearer test_key"}
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "parameters": {"max_tokens": 9999}
    }

    response = client.post("/chat", headers=headers, json=payload)
    assert response.status_code == 400
    assert "exceeds the limit for your tier" in response.json()["detail"]
