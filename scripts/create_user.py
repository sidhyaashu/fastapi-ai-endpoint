import sys
import os
import uuid

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.database.session import SyncSessionLocal
from src.database.models import User, APIKey
from src.utils.logger import logger

def create_user_and_key(db: Session, username: str, budget: float | None = None):
    """Creates a new user and a corresponding API key."""

    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.warn("User already exists", username=username)
        return

    # Create the user
    new_user = User(username=username, monthly_budget=budget)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("Created user", username=new_user.username, user_id=new_user.id, budget=budget)

    # Create an API key for the new user
    plaintext_key = str(uuid.uuid4())
    new_api_key = APIKey(user_id=new_user.id)
    new_api_key.set_key(plaintext_key)

    db.add(new_api_key)
    db.commit()
    db.refresh(new_api_key)

    logger.info("Generated API Key. Please save this key securely; it will not be shown again.")
    print(f"API Key for {username}: {plaintext_key}")

if __name__ == "__main__":
    db = SyncSessionLocal()
    try:
        if len(sys.argv) > 1:
            username = sys.argv[1]
            budget_str = sys.argv[2] if len(sys.argv) > 2 else None
            budget = float(budget_str) if budget_str else None
            create_user_and_key(db, username, budget)
        else:
            print("Usage: python create_user.py <username> [monthly_budget]")
    finally:
        db.close()
