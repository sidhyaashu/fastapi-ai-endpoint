from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Loads and returns a cached sentence-transformer model."""
    # Using a lightweight model for efficiency
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> list[float]:
    """Generates a vector embedding for the given text."""
    model = get_embedding_model()
    return model.encode(text).tolist()
