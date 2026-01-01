import time
import redis
from src import config
from fastapi import HTTPException, status
from functools import lru_cache
from src.utils.logger import logger

@lru_cache(maxsize=1)
def get_redis_client():
    """Returns a Redis client instance, cached for efficiency."""
    return redis.from_url(config.REDIS_URL)

def apply_rate_limit(user_id: str):
    """
    Applies a rate limit to a user, tracked in Redis.
    This function uses the fixed-window counter algorithm.
    """
    redis_client = get_redis_client()
    
    # Determine the correct rate limit configuration for the user
    if user_id == "global_unauthenticated_user":
        rate_limit = config.GLOBAL_RATE_LIMIT
        time_window = config.GLOBAL_TIME_WINDOW_SECONDS
    else:
        # Here you could add logic for tiered access, e.g., fetching user's plan from DB
        rate_limit = config.AUTH_RATE_LIMIT
        time_window = config.AUTH_TIME_WINDOW_SECONDS

    # Create a unique key for the user for the current time window
    current_window = int(time.time() / time_window)
    key = f"rate_limit:{user_id}:{current_window}"
    
    # Use a Redis pipeline to perform the check and increment atomically
    try:
        with redis_client.pipeline() as pipe:
            pipe.incr(key)
            pipe.expire(key, time_window)
            request_count = pipe.execute()[0]
    except redis.exceptions.ConnectionError as e:
        # If Redis is unavailable, we might want to fail open or closed.
        # For this example, we'll fail open (allow the request) but log the error.
        logger.error("Redis connection error during rate limiting", error=str(e))
        return True

    if request_count > rate_limit:
        logger.warn("Rate limit exceeded", user_id=user_id, count=request_count, limit=rate_limit)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

    logger.info("Rate limit check passed", user_id=user_id, count=request_count, limit=rate_limit)
    return True
