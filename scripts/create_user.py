import sys
import os
import uuid

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.database.models import User, APIKey
from src.utils.logger import logger

def create_user_and_key(db: Session, username: str):
    """Creates a new user and a corresponding API key."""

    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.warn("User already exists", username=username)
        return

    # Create the user
    new_user = User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("Created user", username=new_user.username, user_id=new_user.id)

    # Create an API key for the new user
    new_api_key = APIKey(key=str(uuid.uuid4()), user_id=new_user.id)
    db.add(new_api_key)
    db.commit()
    db.refresh(new_api_key)
    logger.info("Generated API Key", api_key=new_api_key.key)

if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Example: Create a user named 'testuser'
        create_user_and_key(db, "testuser")
    finally:
        db.close()
