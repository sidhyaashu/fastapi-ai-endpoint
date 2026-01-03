import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from src.database.models import User, APIKey

pytestmark = pytest.mark.asyncio

async def test_get_user_identifier_no_key(client: TestClient):
    response = client.get("/analytics/report")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

async def test_get_user_identifier_invalid_key(client: TestClient):
    headers = {"Authorization": "Bearer invalid_key"}
    response = client.get("/analytics/report", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"

async def test_get_user_identifier_valid_key(client: TestClient, test_user: User, test_api_key: APIKey):
    headers = {"Authorization": "Bearer test_key"}
    response = client.get("/analytics/report", headers=headers)
    assert response.status_code == 200
    assert response.json()["user_id"] == test_user.id

async def test_scope_enforcement_fail(client: TestClient, db: AsyncSession, test_user: User):
    key_obj = APIKey(user_id=test_user.id, scopes="chat")
    key_obj.set_key("chat_only_key")
    db.add(key_obj)
    await db.commit()

    headers = {"Authorization": "Bearer chat_only_key"}
    response = client.get("/analytics/report", headers=headers)
    assert response.status_code == 403
    assert "analytics" in response.json()["detail"]

@respx.mock
async def test_rate_limit_unauthenticated(client: TestClient):
    respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent").mock(
        return_value=Response(200, json={"candidates": [{"content": {"parts": [{"text": "Mocked response"}]}}]})
    )
    for _ in range(3):
        response = client.post("/chat", json={"messages": [{"role": "user", "content": "test"}]})
        assert response.status_code == 200
    response = client.post("/chat", json={"messages": [{"role": "user", "content": "test"}]})
    assert response.status_code == 429

@respx.mock
async def test_rate_limit_authenticated(client: TestClient, test_user: User, test_api_key: APIKey):
    respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent").mock(
        return_value=Response(200, json={"candidates": [{"content": {"parts": [{"text": "Mocked response"}]}}]})
    )
    headers = {"Authorization": "Bearer test_key"}
    for _ in range(5):
        response = client.post("/chat", headers=headers, json={"messages": [{"role": "user", "content": "test"}]})
        assert response.status_code == 200
    response = client.post("/chat", headers=headers, json={"messages": [{"role": "user", "content": "test"}]})
    assert response.status_code == 429
