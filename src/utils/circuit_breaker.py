import pybreaker
from functools import lru_cache

# Define circuit breaker settings
FAIL_MAX = 5
RESET_TIMEOUT = 60  # seconds

@lru_cache(maxsize=None)
def get_breaker(name: str) -> pybreaker.CircuitBreaker:
    """
    Returns a cached circuit breaker instance for a given name.
    This ensures that each platform gets its own unique breaker.
    """
    return pybreaker.CircuitBreaker(fail_max=FAIL_MAX, reset_timeout=RESET_TIMEOUT)
