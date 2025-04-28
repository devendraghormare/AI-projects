import re
from sqlalchemy import text

def sanitize_sql_query(sql: str) -> str:
    # Remove unwanted non-SQL content like explanations or comments
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)  # Removing comments
    sql = re.sub(r'(\s*This query will return.*)', '', sql)  # Remove non-SQL text (if any)
    return sql.strip()

def execute_query(db, sql: str):
    # Sanitize the SQL query before executing it
    sql = sanitize_sql_query(sql)

    # Wrap the query with text() to explicitly declare it as a raw SQL query
    sql = text(sql)
    
    # Execute the SQL query
    result = db.execute(sql)
    
    # Fetch all the rows and columns
    rows = result.fetchall()
    columns = result.keys()
    
    return rows, columns
