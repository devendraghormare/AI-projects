import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
def test_query_success(mocker):
    # Mock DB session context manager
    mock_db = MagicMock()
    mocker.patch('db.schema_extractor.session.get_db', return_value=mock_db)
    
    # Mock schema extraction
    mocker.patch('db.schema_extractor.schema_extractor.extract_schema', return_value={"tables": ["users"]})
    
    # Mock question optimization (returns same question for simplicity)
    mocker.patch('utils.optimizer.optimize_question', side_effect=lambda q: q)
    
    # Mock cache functions (simulate cache miss for LLM and result)
    mocker.patch('utils.cache.get_cache', side_effect=[None, None])  # LLM cache miss, result cache miss
    mocker.patch('utils.cache.set_cache', return_value=None)
    mocker.patch('utils.cache.make_hash_key', side_effect=lambda x: x)
    
    # Mock async generate_sql to return SQL string inside dict
    mocker.patch('llm.sql_generator.generate_sql', new_callable=AsyncMock,
                 return_value={"sql": "SELECT * FROM users", "token_usage": {"prompt_tokens": 10, "completion_tokens": 5}})
    
    # Mock SQL validator to approve query
    mocker.patch('services.validator.validate_sql', return_value=True)
    
    # Mock SQL execution to return rows and columns
    mocker.patch('db.sql_executor.sql_executor.execute_query', return_value=([("John",)], ["name"]))
    
    # Mock formatter to return a dict with "table" and "json"
    mocker.patch('utils.formatter.format_results', return_value={"table": [["John"]], "json": [{"name": "John"}]})
    
    response = client.post("/v1/query", json={"question": "List users", "allow_modifications": False})

    assert response.status_code == 200
    data = response.json()
    assert "SELECT * FROM users" in data['sql_query']
    assert len(data['results']) > 0


@pytest.mark.asyncio
def test_query_sql_invalid(mocker):
    mock_db = MagicMock()
    mocker.patch('db.schema_extractor.session.get_db', return_value=mock_db)
    mocker.patch('db.schema_extractor.schema_extractor.extract_schema', return_value={"tables": ["users"]})
    mocker.patch('utils.optimizer.optimize_question', side_effect=lambda q: q)
    mocker.patch('utils.cache.get_cache', side_effect=[None])
    mocker.patch('utils.cache.set_cache', return_value=None)
    mocker.patch('utils.cache.make_hash_key', side_effect=lambda x: x)
    mocker.patch('llm.sql_generator.generate_sql', new_callable=AsyncMock,
                 return_value={"sql": "DROP TABLE users", "token_usage": {}})
    
    # Validator returns False indicating unsafe SQL
    mocker.patch('services.validator.validate_sql', return_value=False)
    
    response = client.post("/v1/query", json={"question": "delete everything", "allow_modifications": False})
    
    assert response.status_code == 400
    assert "not safe to execute" in response.json()['detail']


@pytest.mark.asyncio
def test_query_execution_error(mocker):
    mock_db = MagicMock()
    mocker.patch('db.schema_extractor.session.get_db', return_value=mock_db)
    mocker.patch('db.schema_extractor.schema_extractor.extract_schema', return_value={"tables": ["users"]})
    mocker.patch('utils.optimizer.optimize_question', side_effect=lambda q: q)
    mocker.patch('utils.cache.get_cache', side_effect=[None, None])
    mocker.patch('utils.cache.set_cache', return_value=None)
    mocker.patch('utils.cache.make_hash_key', side_effect=lambda x: x)
    mocker.patch('llm.sql_generator.generate_sql', new_callable=AsyncMock,
                 return_value={"sql": "SELECT * FROM users", "token_usage": {}})
    mocker.patch('services.validator.validate_sql', return_value=True)
    
    # Simulate DB error on execute_query
    mocker.patch('db.sql_executor.sql_executor.execute_query', side_effect=Exception("DB connection error"))
    
    response = client.post("/v1/query", json={"question": "Show users", "allow_modifications": False})

    assert response.status_code == 400
    assert "DB connection error" in response.json()["detail"]
