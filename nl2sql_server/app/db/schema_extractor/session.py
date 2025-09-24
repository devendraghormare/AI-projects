from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from core.config import settings 
from sqlalchemy.pool import QueuePool 

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,           # Number of connections to keep in the pool
    max_overflow=settings.DB_MAX_OVERFLOW,     # Extra connections beyond pool_size
    pool_timeout=settings.DB_POOL_TIMEOUT,     # Wait time (in seconds) for getting a connection
    pool_recycle=settings.DB_POOL_RECYCLE,     # Recycle connections after 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  
