import pytest
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.sql_executor.sql_executor import execute_query

logger = logging.getLogger(__name__)

# Setup in-memory SQLite for testing
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db():
    with SessionLocal() as session:
        yield session

def setup_dummy_table(db):
    logger.info("Setting up dummy table for testing.")
    
    # Drop the table if it already exists to avoid conflicts
    db.execute(text("DROP TABLE IF EXISTS test"))
    
    # Now create the table
    db.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
    db.execute(text("INSERT INTO test (name) VALUES ('Alice'), ('Bob')"))
    db.commit()
    
    logger.info("Dummy table setup complete.")

def test_execute_simple_select(db):
    logger.info("\n\n--- Test Started: Execute Simple Select ---")
    
    setup_dummy_table(db)
    rows, columns = execute_query(db, "SELECT * FROM test")
    
    assert len(rows) == 2
    assert "id" in columns and "name" in columns
    
    logger.info("Test Passed: Execute Simple Select. Rows and columns as expected.")
    
    logger.info("--- Test Ended: Execute Simple Select ---\n\n")

def test_execute_empty_result(db):
    logger.info("\n\n--- Test Started: Execute Empty Result ---")
    
    setup_dummy_table(db)
    rows, columns = execute_query(db, "SELECT * FROM test WHERE id = 999")
    
    assert rows == []
    
    logger.info("Test Passed: Execute Empty Result. Empty result as expected.")
    
    logger.info("--- Test Ended: Execute Empty Result ---\n\n")

def test_execute_invalid_sql(db):
    logger.info("\n\n--- Test Started: Execute Invalid SQL ---")
    
    with pytest.raises(Exception):
        execute_query(db, "SELECT * FROM non_existing_table")
    
    logger.info("Test Passed: Execute Invalid SQL. Exception raised as expected.")
    
    logger.info("--- Test Ended: Execute Invalid SQL ---\n\n")
