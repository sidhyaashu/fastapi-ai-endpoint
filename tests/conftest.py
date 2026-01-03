import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database.session import get_db
from src.database.models import Base, User, APIKey

# Use an in-memory SQLite database for testing
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = AsyncTestingSessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(db: AsyncSession) -> TestClient:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    user = User(id="test_user", username="testuser", tier="free")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture(scope="function")
async def test_api_key(db: AsyncSession, test_user: User) -> APIKey:
    key_obj = APIKey(user_id=test_user.id, scopes="chat analytics")
    key_obj.set_key("test_key")
    db.add(key_obj)
    await db.commit()
    await db.refresh(key_obj)
    return key_obj
