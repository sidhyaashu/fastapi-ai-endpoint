import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, APIKey, UsageLog

pytestmark = pytest.mark.asyncio

async def test_analytics_report_no_data(client: TestClient, test_user: User, test_api_key: APIKey):
    headers = {"Authorization": "Bearer test_key"}
    response = client.get("/analytics/report", headers=headers)

    assert response.status_code == 200
    report = response.json()
    assert report["user_id"] == test_user.id
    assert report["summary"]["total_requests"] == 0

async def test_analytics_report_with_data(client: TestClient, db: AsyncSession, test_user: User, test_api_key: APIKey):
    log = UsageLog(user_id=test_user.id, platform="gemini", prompt_tokens=10, completion_tokens=20, total_tokens=30, latency_ms=100, cost=0.001)
    db.add(log)
    await db.commit()

    headers = {"Authorization": "Bearer test_key"}
    response = client.get("/analytics/report", headers=headers)

    assert response.status_code == 200
    report = response.json()
    assert report["summary"]["total_requests"] == 1
    assert report["summary"]["total_cost"] == 0.001

async def test_budget_enforcement(client: TestClient, db: AsyncSession, test_user: User, test_api_key: APIKey):
    test_user.monthly_budget = 10.0
    test_user.monthly_spending = 10.0
    db.add(test_user)
    await db.commit()

    headers = {"Authorization": "Bearer test_key"}
    payload = {"messages": [{"role": "user", "content": "This should fail"}]}

    response = client.post("/chat", headers=headers, json=payload)
    assert response.status_code == 429
    assert "Monthly budget exceeded" in response.json()["detail"]
