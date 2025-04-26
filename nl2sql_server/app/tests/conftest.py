import logging
import pytest

@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler("tests/test_log.txt"),
            logging.StreamHandler()
        ]
    )
