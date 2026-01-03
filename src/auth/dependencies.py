from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from src.database.session import get_db
from src.database.models import APIKey, User
from src.utils.logger import logger

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_db_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> APIKey:
    """Dependency to get the APIKey object from a raw token."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Authentication required")

    parts = api_key.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    token = parts[1]

    if len(token) < 8:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    prefix = token[:8]
    result = await db.execute(select(APIKey).where(APIKey.key_prefix == prefix))
    db_api_key = result.scalars().first()

    if not db_api_key or not db_api_key.verify_key(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    return db_api_key

async def get_user_identifier(
    db_api_key: APIKey = Depends(get_db_api_key)
) -> str:
    """Dependency to get the user_id from the APIKey object."""
    if not db_api_key:
        return "global_unauthenticated_user" # Should not happen due to checks in get_db_api_key
    return db_api_key.user_id

async def get_current_user(
    user_id: str = Depends(get_user_identifier),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if user_id == "global_unauthenticated_user":
        return None
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found for API key")
    return user

async def enforce_budget(user: User | None = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user or user.monthly_budget is None:
        return

    now = datetime.utcnow()
    last_reset = user.last_usage_reset.replace(tzinfo=None) if user.last_usage_reset.tzinfo else user.last_usage_reset

    if (now - last_reset) > timedelta(days=30):
        logger.info("Resetting monthly spending for user", user_id=user.id)
        user.monthly_spending = 0.0
        user.last_usage_reset = now
        await db.commit()

    if user.monthly_spending >= user.monthly_budget:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Monthly budget exceeded. Please contact support.",
        )

def require_scope(required_scope: str):
    """
    FastAPI dependency to protect an endpoint with a required scope.
    This check is based ONLY on the scopes stored in the APIKey.
    """
    async def scope_checker(
        db_api_key: APIKey = Depends(get_db_api_key)
    ):
        if required_scope not in db_api_key.scopes.split():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key does not have the required '{required_scope}' scope.",
            )

    return scope_checker
