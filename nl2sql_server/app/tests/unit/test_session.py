import pytest
import logging
from sqlalchemy import text
from db.schema_extractor.session import get_db

logger = logging.getLogger(__name__)

def test_get_db_session_works():
    logger.info("\n\n--- Test Started: DB Session Works ---")

    with get_db() as db:
        logger.info("DB session started. Session: %s", db)

        # Proper way to run raw SQL in SQLAlchemy
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1

        logger.info("DB session executed a test query successfully.")

    logger.info("--- Test Ended: DB Session Works ---\n\n")
