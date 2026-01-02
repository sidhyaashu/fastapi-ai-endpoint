from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src import config

# Create the SQLAlchemy async engine
engine = create_async_engine(config.ASYNC_DATABASE_URL, echo=True)

# Create a configured "AsyncSession" class
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    """
    FastAPI dependency to get an async database session.
    Ensures the session is closed after the request is finished.
    """
    async with AsyncSessionLocal() as session:
        yield session
