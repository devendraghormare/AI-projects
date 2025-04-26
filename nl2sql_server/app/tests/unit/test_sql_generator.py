import pytest
import logging
from unittest.mock import AsyncMock, patch
from llm.sql_generator import generate_sql

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_generate_sql_success():
    logger.info("\n\n--- Test Started: Generate SQL Success ---")

    # Mocking the OpenAI response with AsyncMock
    fake_response = AsyncMock()
    fake_response.choices = [AsyncMock()]
    fake_response.choices[0].message.content = "SELECT * FROM users;"

    # Ensure the mock client is set up to return a coroutine (to be awaited)
    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create = AsyncMock(return_value=fake_response)

        # Calling the generate_sql function
        result = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key"
        )

        # Asserting the expected results
        assert "SELECT" in result
        assert "users" in result

        logger.info("Test Passed: Generate SQL Success. SQL query generated as expected.")
        
    logger.info("--- Test Ended: Generate SQL Success ---\n\n")

@pytest.mark.asyncio
async def test_generate_sql_api_error():
    logger.info("\n\n--- Test Started: Generate SQL API Error ---")

    # Simulating an API error response
    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = mock_openai.return_value
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Calling the generate_sql function with the mocked error
        result = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key"
        )

        # Asserting the error handling
        assert "Error" in result

        logger.info("Test Passed: Generate SQL API Error. Error handled correctly.")
    
    logger.info("--- Test Ended: Generate SQL API Error ---\n\n")

@pytest.mark.asyncio
async def test_generate_sql_general_exception():
    logger.info("\n\n--- Test Started: Generate SQL General Exception ---")

    # Simulating a random error in the OpenAI API call
    with patch("openai.AsyncOpenAI", side_effect=Exception("Some random error")):
        result = await generate_sql(
            question="List all users",
            schema="Table users: id (integer), name (text)",
            api_key="fake-api-key"
        )

        # Asserting the error handling
        assert "Error" in result

        logger.info("Test Passed: Generate SQL General Exception. Exception handled correctly.")
    
    logger.info("--- Test Ended: Generate SQL General Exception ---\n\n")
