import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from llm.sql_generator import generate_sql

@pytest.mark.asyncio
async def test_generate_sql_success():
    # Prepare a fake response object with choices and usage (usage as MagicMock with attributes)
    fake_usage = MagicMock()
    fake_usage.prompt_tokens = 100
    fake_usage.completion_tokens = 20
    fake_usage.total_tokens = 120

    choice_mock = MagicMock()
    choice_mock.message.content = "SELECT * FROM users;"

    fake_response = MagicMock()
    fake_response.choices = [choice_mock]
    fake_response.usage = fake_usage

    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=fake_response)

        # Call generate_sql without usage info
        result = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key",
            return_usage=False
        )
        assert isinstance(result, str)
        assert "SELECT" in result
        assert "users" in result

        # Call generate_sql with usage info
        result_with_usage = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key",
            return_usage=True
        )
        assert isinstance(result_with_usage, dict)
        assert "sql" in result_with_usage
        assert "token_usage" in result_with_usage
        assert result_with_usage["sql"] == "SELECT * FROM users;"
        assert result_with_usage["token_usage"]["total_tokens"] == 120

@pytest.mark.asyncio
async def test_generate_sql_api_error():
    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        
        class DummyAPIError(Exception):
            pass

        mock_client.chat.completions.create.side_effect = DummyAPIError("API error")

        result = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key"
        )
        assert isinstance(result, dict)
        assert result.get("status") == "error"
        assert "API" in result.get("message", "")

@pytest.mark.asyncio
async def test_generate_sql_general_exception():
    with patch("openai.AsyncOpenAI", side_effect=Exception("Some random error")):
        result = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key"
        )
        assert isinstance(result, dict)
        assert result.get("status") == "error"
        assert "Some random error" in result.get("message", "")
