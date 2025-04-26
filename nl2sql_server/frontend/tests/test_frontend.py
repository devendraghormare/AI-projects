import time
import pytest
from streamlit.testing import TestStreamlit
from unittest.mock import patch
import requests

# Mock requests.post to simulate backend interaction
def mock_requests_post(url, json, headers):
    # Simulating the backend response for SQL query generation
    if url == "http://localhost:8000/v1/query":
        return MockResponse({
            "sql_query": "SELECT * FROM users WHERE age > 30;",
            "results": [{"id": 1, "name": "John Doe", "age": 35}]
        })
    return MockResponse(None)

class MockResponse:
    def __init__(self, json_data):
        self.json_data = json_data
        self.status_code = 200

    def json(self):
        return self.json_data

# Test case to ensure Streamlit elements are loading
def test_render_streamlit_app():
    # Start the Streamlit app
    app = TestStreamlit()
    
    # Check the sidebar components (Question input and button)
    app.sidebar.text_input("Enter your question:")
    app.sidebar.checkbox("Allow SQL Modifications")
    app.sidebar.button("🧹 Clear Results")
    app.sidebar.button("🔎 Submit Query")
    
    # Verify that page elements are loaded
    app.sidebar.assert_has_text("SQL Query Tester")
    app.sidebar.assert_has_text("🧠 Provide a natural language question:")

    # Check the main page for the "Generated SQL" and "Query Results" sections
    app.assert_has_text("🚀 SQL Query Generator & Executor")
    app.assert_has_text("### 📝 Generated SQL Query:")
    app.assert_has_text("### 📊 Query Results:")

# Test case to simulate user input and backend query response
@patch("requests.post", side_effect=mock_requests_post)
def test_submit_query(mock_post):
    app = TestStreamlit()

    # Simulate the user input
    app.sidebar.text_input("Enter your question:", value="Get users older than 30")
    app.sidebar.button("🔎 Submit Query")

    # Wait a bit for the API response and the UI to update
    time.sleep(2)

    # Check if the correct SQL query was displayed
    app.assert_has_text("### 📝 Generated SQL Query:")
    app.assert_has_text("SELECT * FROM users WHERE age > 30;")

    # Check if the query results are displayed as a table
    app.assert_has_text("### 📊 Query Results:")
    app.assert_has_text("John Doe")  # Example name in the results

# Test case to check the functionality of the "Clear Results" button
@patch("requests.post", side_effect=mock_requests_post)
def test_clear_results(mock_post):
    app = TestStreamlit()

    # Simulate the user input and submit the query
    app.sidebar.text_input("Enter your question:", value="Get users older than 30")
    app.sidebar.button("🔎 Submit Query")
    
    # Wait for the UI to update
    time.sleep(2)

    # Check if the generated SQL and results are displayed
    app.assert_has_text("### 📝 Generated SQL Query:")
    app.assert_has_text("SELECT * FROM users WHERE age > 30;")
    app.assert_has_text("### 📊 Query Results:")
    
    # Simulate clicking the "Clear Results" button
    app.sidebar.button("🧹 Clear Results")

    # Check if the results have been cleared
    app.assert_not_has_text("### 📝 Generated SQL Query:")
    app.assert_not_has_text("### 📊 Query Results:")

# Test case to check error handling when the backend fails
@patch("requests.post", side_effect=lambda url, json, headers: MockResponse(None))
def test_backend_error(mock_post):
    app = TestStreamlit()

    # Simulate the user input and submit the query
    app.sidebar.text_input("Enter your question:", value="Get users older than 30")
    app.sidebar.button("🔎 Submit Query")

    # Wait for the API to return
    time.sleep(2)

    # Check if the error message is displayed
    app.assert_has_text("Error: No SQL query generated.")
    app.assert_has_text("Error: No results returned from the query.")
