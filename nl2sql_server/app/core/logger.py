from loguru import logger
import os

def setup_logging():
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        logger.remove()

        # General query execution log
        logger.add(
            os.path.join(log_dir, "query_execution.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="1 week",
            retention="4 weeks",
            compression="zip"
        )

        # LLM log
        logger.add(
            os.path.join(log_dir, "llm.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="1 week",
            retention="4 weeks",
            compression="zip",
            filter=lambda record: "llm" in record["extra"]
        )

        # SQL executor log
        logger.add(
            os.path.join(log_dir, "sql_executor.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="1 week",
            retention="4 weeks",
            compression="zip",
            filter=lambda record: "sql_executor" in record["extra"]
        )
        # Schema extractorr log
        logger.add(
            os.path.join(log_dir, "schema_extractor.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="1 week",
            retention="4 weeks",
            compression="zip",
            filter=lambda record: "schema_extractor" in record["extra"]
        )

    except Exception:
        pass
