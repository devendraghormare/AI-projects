import sqlparse
import re

def sanitize_sql_for_validation(sql: str) -> str:
    # Remove any non-SQL content
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)  # Removing comments
    sql = re.sub(r'(\s*This query will return.*)', '', sql)  # Remove non-SQL text
    return sql.strip()

def validate_sql(sql: str, allow_modifications: bool = False) -> bool:
    dangerous = ["DROP", "DELETE", "ALTER", "INSERT", "UPDATE"]
    sql = sanitize_sql_for_validation(sql)  # Clean the query before validation

    statements = sqlparse.parse(sql)
    tokens = [token.value.upper() for stmt in statements for token in stmt.tokens if token.ttype]

    if not allow_modifications:
        if any(danger in token for danger in dangerous for token in tokens):
            return False
    return True
