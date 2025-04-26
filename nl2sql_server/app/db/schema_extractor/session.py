from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from core.config import settings  

# Create an engine using the DATABASE_URL from settings
engine = create_engine(settings.DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use context management for proper session handling
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  
