import time
import redis
from src import config
from fastapi import Depends, HTTPException, status
from functools import lru_cache
from sqlalchemy.orm import Session
from src.utils.logger import logger
from src.database.session import get_db
from src.database.models import User
from src.auth.dependencies import get_user_identifier

@lru_cache(maxsize=1)
def get_redis_client():
    """Returns a Redis client instance, cached for efficiency."""
    return redis.from_url(config.REDIS_URL)

def get_current_user(user_id: str = Depends(get_user_identifier), db: Session = Depends(get_db)) -> User | None:
    """FastAPI dependency to get the current user from the database."""
    if user_id == "global_unauthenticated_user":
        return None
    return db.query(User).filter(User.id == user_id).first()

def apply_rate_limit(user: User | None = Depends(get_current_user)):
    """
    Applies a rate limit to a user, tracked in Redis.
    This function uses the fixed-window counter algorithm.
    """
    redis_client = get_redis_client()
    
    if user:
        # Tiered rate limits for authenticated users
        if user.tier == "pro":
            rate_limit = 100
            time_window = 60
        elif user.tier == "enterprise":
            rate_limit = 1000
            time_window = 60
        else: # "free" tier
            rate_limit = config.AUTH_RATE_LIMIT
            time_window = config.AUTH_TIME_WINDOW_SECONDS
        user_id = user.id
    else:
        # Default limits for unauthenticated users
        rate_limit = config.GLOBAL_RATE_LIMIT
        time_window = config.GLOBAL_TIME_WINDOW_SECONDS
        user_id = "global_unauthenticated_user"

    current_window = int(time.time() / time_window)
    key = f"rate_limit:{user_id}:{current_window}"
    
    try:
        with redis_client.pipeline() as pipe:
            pipe.incr(key)
            pipe.expire(key, time_window)
            request_count = pipe.execute()[0]
    except redis.exceptions.ConnectionError as e:
        logger.error("Redis connection error during rate limiting", error=str(e))
        return

    if request_count > rate_limit:
        logger.warn("Rate limit exceeded", user_id=user_id, count=request_count, limit=rate_limit)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

    logger.info("Rate limit check passed", user_id=user_id, count=request_count, limit=rate_limit)
