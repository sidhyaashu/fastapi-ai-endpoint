from celery import Celery
from src import config
from src.database.session import SyncSessionLocal
from src.database.models import User, UsageLog
from src.utils.cost_calculator import calculate_cost
from src.schema import TokenUsage

# Configure Celery
celery_app = Celery("tasks", broker=config.REDIS_URL, backend=config.REDIS_URL)

@celery_app.task
def log_usage_task(user_id: str, platform: str, token_usage_dict: dict, latency_ms: float, model_name: str):
    """
    Celery task to log API usage asynchronously using a synchronous database session.
    """
    db = SyncSessionLocal()
    try:
        token_usage = TokenUsage(**token_usage_dict)
        cost = calculate_cost(model_name, token_usage)

        # Log the usage event
        log_entry = UsageLog(
            user_id=user_id, platform=platform, prompt_tokens=token_usage.prompt_tokens,
            completion_tokens=token_usage.completion_tokens, total_tokens=token_usage.total_tokens,
            latency_ms=latency_ms, cost=cost
        )
        db.add(log_entry)

        # Update user's monthly spending
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.monthly_spending += cost

        db.commit()
    finally:
        db.close()
