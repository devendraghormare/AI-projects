from sqlalchemy import inspect

def extract_schema(db):
    # Use the engine, not the session
    inspector = inspect(db.bind)  # db.bind will give you the engine bound to the session
    schema_str = ""
    for table_name in inspector.get_table_names():
        schema_str += f"Table {table_name}:\n"
        columns = inspector.get_columns(table_name)
        for column in columns:
            schema_str += f"  - {column['name']} ({column['type']})\n"
    return schema_str
