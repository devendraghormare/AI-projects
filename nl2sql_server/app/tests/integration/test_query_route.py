import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from main import app

client = TestClient(app)
logger = logging.getLogger(__name__)

def test_query_success(mocker):
    logger.info(f"\n\n--- Test Started: Query Success ---")
    
    mocker.patch('llm.sql_generator.generate_sql', return_value="SELECT * FROM users")
    mocker.patch('db.sql_executor.sql_executor.execute_query', return_value=([("John",)], ["name"]))
    
    logger.info("Sending request: List users")
    response = client.post("/v1/query", json={"question": "List users", "allow_modifications": False})
    
    assert response.status_code == 200
    data = response.json()
    
    logger.info(f"Response received: {data}")
    assert "SELECT * FROM users" in data['sql_query']
    assert len(data['results']) > 0
    
    logger.info("--- Test Ended: Query Success ---\n\n")


def test_query_sql_invalid(mocker):
    logger.info(f"\n\n--- Test Started: Query SQL Invalid ---")
    
    mocker.patch('llm.sql_generator.generate_sql', return_value="DROP TABLE users")
    
    logger.info("Sending request: delete everything")
    response = client.post("/v1/query", json={"question": "delete everything", "allow_modifications": False})
    
    assert response.status_code == 400
    logger.info(f"Error response received: {response.json()}")
    assert "not safe to execute" in response.json()['detail']
    
    logger.info("--- Test Ended: Query SQL Invalid ---\n\n")


def test_query_execution_error(mocker):
    logger.info(f"\n\n--- Test Started: Query Execution Error ---")

    # Mocking SQL generation to return a valid query
    mocker.patch('llm.sql_generator.generate_sql', new_callable=AsyncMock, return_value="SELECT * FROM users")
    
    # Patch execute_query where it's used in the FastAPI route
    mocker.patch('api.v1.endpoints.query.execute_query', side_effect=Exception("DB connection error"))

    logger.info("Sending request: Show users")
    response = client.post("/v1/query", json={"question": "Show users", "allow_modifications": False})

    logger.info(f"Response content: {response.text}")

    # Check that we receive a 400 error and the expected message
    assert response.status_code == 400
    assert "DB connection error" in response.json()["detail"]

    logger.info("--- Test Ended: Query Execution Error ---\n\n")

