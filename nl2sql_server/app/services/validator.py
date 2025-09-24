import sqlparse
import re

def sanitize_sql_for_validation(sql: str) -> str:
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)  
    sql = re.sub(r'(\s*This query will return.*)', '', sql)  
    return sql.strip()

def validate_sql(sql: str, allow_modifications: bool = False) -> bool:
    dangerous = ["DROP", "DELETE", "ALTER", "INSERT", "UPDATE"]
    sql = sanitize_sql_for_validation(sql) 

    statements = sqlparse.parse(sql)
    tokens = [token.value.upper() for stmt in statements for token in stmt.tokens if token.ttype]

    if not allow_modifications:
        if any(danger in token for token in tokens for danger in dangerous):
            return False

    return True
