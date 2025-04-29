import re
from sqlalchemy import text
from loguru import logger

sql_logger = logger.bind(sql_executor=True)

def sanitize_sql_query(sql: str) -> str:
    try:
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'(\s*This query will return.*)', '', sql)
        return sql.strip()
    except Exception as e:
        sql_logger.error(f"Error during SQL sanitization: {e}")
        raise

def execute_query(db, sql: str):
    try:
        sql_logger.info(f"Raw SQL before sanitization: {sql}")
        sql = sanitize_sql_query(sql)
        sql_logger.info(f"Sanitized SQL: {sql}")

        sql = text(sql)
        result = db.execute(sql)

        if result.returns_rows:
            rows = result.fetchall()
            columns = result.keys()
            sql_logger.info(f"Query executed successfully. Rows fetched: {len(rows)}")
        else:
            rows = []
            columns = []
            sql_logger.info("Query executed successfully. No rows returned (e.g. DML operation).")

        return rows, columns

    except Exception as e:
        sql_logger.error(f"SQL execution error: {e}")
        raise
