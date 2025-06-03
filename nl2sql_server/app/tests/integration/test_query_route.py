import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from unittest.mock import AsyncMock
from main import app 
import json
client = TestClient(app)

# -------------------------------
#  SUCCESS: Valid SELECT Query
# -------------------------------
@patch("app.api.v1.endpoints.query.set_cache")
@patch("app.api.v1.endpoints.query.get_cache")
@patch("app.api.v1.endpoints.query.execute_query")
@patch("app.api.v1.endpoints.query.validate_sql")
@patch("app.api.v1.endpoints.query.generate_sql", new_callable=AsyncMock)
@patch("app.api.v1.endpoints.query.extract_schema")
@patch("app.api.v1.endpoints.query.get_db")
def test_generate_and_execute_query_success(
    mock_get_db,
    mock_extract_schema,
    mock_generate_sql,
    mock_validate_sql,
    mock_execute_query,
    mock_get_cache,
    mock_set_cache
):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    mock_extract_schema.return_value = {"tables": {"users": ["id", "name", "email"]}}

    mock_generate_sql.return_value = {
        "sql": "SELECT COUNT(*) FROM users;",
        "token_usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }

    mock_validate_sql.return_value = True
    mock_get_cache.return_value = None
    mock_execute_query.return_value = ([("201.00",)], ["count"])

    response = client.post("/v1/query", json={
        "question": "How many users?",
        "allow_modifications": False
    })

    assert response.status_code == 200
    data = response.json()
    assert data["sql_query"] == "SELECT COUNT(*) FROM users;"
    assert data["results"][0]["count"] == "201.00"
    assert "token_usage" in data



# --------------------------------------
#  ERROR: Unsafe SQL Query Blocked
# --------------------------------------
@patch("app.api.v1.endpoints.query.get_db")
@patch("app.api.v1.endpoints.query.extract_schema")
@patch("app.api.v1.endpoints.query.generate_sql")
@patch("app.api.v1.endpoints.query.validate_sql")
def test_generate_and_execute_query_invalid_sql(
    mock_validate_sql,
    mock_generate_sql,
    mock_extract_schema,
    mock_get_db,
):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    mock_extract_schema.return_value = {"tables": {"users": ["id", "name"]}}
    mock_generate_sql.return_value = {"sql": "DROP TABLE users;", "token_usage": {}}
    mock_validate_sql.return_value = False

    response = client.post("/v1/query", json={
        "question": "Drop the users table?",
        "allow_modifications": False
    })

    assert response.status_code == 400
    assert "not safe to execute" in response.json()["detail"]


# ----------------------------
#  CACHE HIT for LLM Output
# ----------------------------
@patch("app.api.v1.endpoints.query.get_db")
@patch("app.api.v1.endpoints.query.extract_schema")
@patch("app.api.v1.endpoints.query.get_cache")
@patch("app.api.v1.endpoints.query.validate_sql")
@patch("app.api.v1.endpoints.query.execute_query")
def test_generate_query_with_llm_cache_hit(
    mock_execute_query,
    mock_validate_sql,
    mock_get_cache,
    mock_extract_schema,
    mock_get_db,
):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db

    mock_extract_schema.return_value = {"tables": {"products": ["id", "name"]}}
    cached_llm = {
        "sql": "SELECT * FROM products;",
        "token_usage": {"prompt_tokens": 5, "completion_tokens": 10}
    }
    mock_get_cache.side_effect = [json.dumps(cached_llm), None]  # LLM hit, result miss

    mock_validate_sql.return_value = True
    mock_execute_query.return_value = ([("4K TV",)], ["name"])

    response = client.post("/v1/query", json={
        "question": "Show all products",
        "allow_modifications": False
    })

    assert response.status_code == 200
    assert response.json()["sql_query"] == "SELECT * FROM products;"
    assert response.json()["results"][0]["name"] == "4K TV"



# ----------------------------
#  Non-SELECT Query (e.g. UPDATE)
# ----------------------------
@patch("app.api.v1.endpoints.query.get_db")
@patch("app.api.v1.endpoints.query.extract_schema")
@patch("app.api.v1.endpoints.query.generate_sql")
@patch("app.api.v1.endpoints.query.validate_sql")
@patch("app.api.v1.endpoints.query.execute_query")
@patch("app.api.v1.endpoints.query.get_cache")
def test_generate_and_execute_update_query(
    mock_get_cache,
    mock_execute_query,
    mock_validate_sql,
    mock_generate_sql,
    mock_extract_schema,
    mock_get_db,
):
    mock_db = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_db
    mock_extract_schema.return_value = {"tables": {"users": ["id", "name"]}}

    mock_generate_sql.return_value = {
        "sql": "UPDATE users SET name='John' WHERE id=1;",
        "token_usage": {}
    }

    mock_validate_sql.return_value = True
    mock_get_cache.return_value = None
    mock_execute_query.return_value = ([], [])  # UPDATE returns no rows

    response = client.post("/v1/query", json={
        "question": "Change user 1 name to John",
        "allow_modifications": True
    })

    assert response.status_code == 200
    assert response.json()["sql_query"].startswith("UPDATE users")

