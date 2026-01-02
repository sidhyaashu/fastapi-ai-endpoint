from src.schema import TokenUsage

# --- Pricing (in USD per 1,000,000 tokens) ---
# These are example prices and should be updated regularly
MODEL_PRICING = {
    # OpenAI
    "gpt-4": {"prompt": 30.0, "completion": 60.0},
    # Anthropic
    "claude-3-opus-20240229": {"prompt": 15.0, "completion": 75.0},
    # Google
    "gemini-1.5-flash": {"prompt": 0.7, "completion": 2.1},
    # Groq (often free for basic use, but we can assign a value for tracking)
    "llama3-8b-8192": {"prompt": 0.1, "completion": 0.1},
}

def calculate_cost(model_name: str, token_usage: TokenUsage) -> float | None:
    """
    Calculates the estimated cost of an AI request.
    Returns the cost in USD or None if pricing is not available.
    """
    pricing = MODEL_PRICING.get(model_name)
    if not pricing:
        return None

    prompt_cost = (token_usage.prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (token_usage.completion_tokens / 1_000_000) * pricing["completion"]

    return prompt_cost + completion_cost
