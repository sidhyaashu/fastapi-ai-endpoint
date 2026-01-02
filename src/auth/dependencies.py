from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.session import get_db
from src.database.models import APIKey, User

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_user_identifier(
    api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> str:
    if not api_key:
        return "global_unauthenticated_user"

    # The key is expected to be "Bearer <key>"
    parts = api_key.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return "global_unauthenticated_user"

    token = parts[1]

    result = await db.execute(select(APIKey).where(APIKey.key == token))
    db_api_key = result.scalars().first()

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    return db_api_key.user_id

async def get_current_user(
    user_id: str = Depends(get_user_identifier),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if user_id == "global_unauthenticated_user":
        return None
    return await db.get(User, user_id)
