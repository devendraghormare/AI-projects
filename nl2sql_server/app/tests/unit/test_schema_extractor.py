import pytest
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.schema_extractor.schema_extractor import extract_schema

logger = logging.getLogger(__name__)

# Setup in-memory SQLite for testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    with SessionLocal() as session:
        yield session

def setup_dummy_schema(db):
    logger.info("Creating dummy schema...")
    db.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"))
    db.commit()
    logger.info("Dummy schema created with 'users' table.")

def test_extract_schema_success(db):
    logger.info("\n\n--- Test Started: Extract Schema Success ---")
    
    setup_dummy_schema(db)
    
    logger.info("Extracting schema...")
    schema_str = extract_schema(db)
    
    logger.info("Extracted Schema: \n%s", schema_str)
    
    assert "Table users:" in schema_str
    assert "id" in schema_str
    assert "name" in schema_str
    assert "email" in schema_str
    
    logger.info("--- Test Ended: Extract Schema Success ---\n\n")
