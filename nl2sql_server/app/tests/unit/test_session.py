import pytest
import logging
from db.schema_extractor.session import get_db

logger = logging.getLogger(__name__)

def test_get_db_session_works():
    logger.info("\n\n--- Test Started: DB Session Works ---")
    
    with get_db() as db:
        logger.info("DB session started. Active: %s", db.is_active)
        assert db is not None
        assert db.is_active
        logger.info("DB session is active and valid.")
    
    logger.info("--- Test Ended: DB Session Works ---\n\n")
