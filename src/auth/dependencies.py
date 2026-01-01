from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.database.models import APIKey, User

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_user_identifier(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> str:
    if not api_key:
        return "global_unauthenticated_user"

    # The key is expected to be "Bearer <key>"
    parts = api_key.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return "global_unauthenticated_user" # or raise an exception for malformed header

    token = parts[1]

    # Check the database for the API key
    db_api_key = db.query(APIKey).filter(APIKey.key == token).first()

    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    # Return the user_id associated with the key
    return db_api_key.user_id
