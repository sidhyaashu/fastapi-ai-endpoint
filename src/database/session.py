from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import config

# Create the SQLAlchemy engine
engine = create_engine(config.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency to get a database session.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
