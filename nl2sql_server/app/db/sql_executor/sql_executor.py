from sqlalchemy import text

def execute_query(db, sql: str):
    # Wrap the query with text() to explicitly declare it as a raw SQL query
    sql = text(sql)
    
    # Execute the SQL query
    result = db.execute(sql)
    
    # Fetch all the rows and columns
    rows = result.fetchall()
    columns = result.keys()
    
    return rows, columns
