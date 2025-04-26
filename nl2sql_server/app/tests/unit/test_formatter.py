import pytest
import logging
from utils.formatter import format_results

# Create logger
logger = logging.getLogger(__name__)

def test_single_row_single_column():
    rows = [('John',)]
    columns = ['name']
    result = format_results(rows, columns)

    logger.info(f"Testing single row: {result}")
    
    assert "John" in result['table']
    assert result['json'] == [{"name": "John"}]

def test_multiple_rows_multiple_columns():
    rows = [('John', 30), ('Jane', 25)]
    columns = ['name', 'age']
    result = format_results(rows, columns)

    logger.info(f"Testing multiple rows: {result}")

    assert "John" in result['table'] and "Jane" in result['table']
    assert result['json'] == [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]

def test_empty_result():
    rows = []
    columns = ['id', 'name']
    result = format_results(rows, columns)

    logger.info(f"Testing empty result: {result}")

    assert "No data found" in result['table'] or len(result['json']) == 0
