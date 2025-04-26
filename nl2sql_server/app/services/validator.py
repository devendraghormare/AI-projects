import sqlparse

def validate_sql(sql: str, allow_modifications: bool = False) -> bool:
    dangerous = ["DROP", "DELETE", "ALTER", "INSERT", "UPDATE"]
    statements = sqlparse.parse(sql)
    tokens = [token.value.upper() for stmt in statements for token in stmt.tokens if token.ttype]

    if not allow_modifications:
        if any(danger in token for danger in dangerous for token in tokens):
            return False
    return True
