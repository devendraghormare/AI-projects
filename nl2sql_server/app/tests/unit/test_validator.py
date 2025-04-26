import pytest
import logging
from services.validator import validate_sql

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("sql_query, allow_modifications, expected_result", [
    ("SELECT * FROM users", False, True),
    ("DROP TABLE users", False, False),
    ("DELETE FROM users WHERE id=1", False, False),
    ("INSERT INTO users (name) VALUES ('John')", False, False),
    ("UPDATE users SET name='Jane' WHERE id=1", False, False),
    ("DROP TABLE users", True, True),
    ("SeLeCt name FROM users", False, True),  # case-insensitive check
])
def test_validate_sql(sql_query, allow_modifications, expected_result):
    logger.info(f"\n\n--- Test Started: Validate SQL ---")
    logger.info(f"Testing query: {sql_query}, Allow modifications: {allow_modifications}")
    
    result = validate_sql(sql_query, allow_modifications)
    
    assert result == expected_result
    
    logger.info(f"Test Passed: Query validation result is {result}")
    logger.info("--- Test Ended: Validate SQL ---\n\n")
