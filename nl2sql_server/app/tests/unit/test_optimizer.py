# tests/unit/test_optimizer.py

import pytest
import logging
from utils.optimizer import optimize_question

logger = logging.getLogger(__name__)

@pytest.mark.parametrize("input_question, expected_output", [
    ("show me top 5 prdct by sales", "show me top 5 product by sales?"),
    ("list all usr who placed an ordr last month", "list all user who placed an order last month?"),
    ("what is avg amt spent by each usr", "what is average amount spent by each user?"),
    ("   how many products are out of stock    ", "how many products are out of stock?"),
    ("cnt of ordr by usr in last week", "count of order by user in last week?"),
    ("how many users registered today?", "how many users registered today?"),
])
def test_optimize_question(input_question, expected_output):
    logger.info("\n\n--- Test Started ---")
    logger.info("\n🔵 Input Question: %s\n🟢 Optimized Question: %s\n🟡 Expected Output: %s", 
                input_question, expected_output, expected_output)
    
    optimized = optimize_question(input_question)
    
    logger.info("\n🔵 Input Question: %s\n🟢 Optimized Question: %s\n🟡 Expected Output: %s", 
                input_question, optimized, expected_output)
    
    assert optimized == expected_output
    logger.info("\n--- Test Ended ---\n\n")
