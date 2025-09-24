from sqlalchemy import inspect
from loguru import logger

schema_logger = logger.bind(schema_extractor=True)

def extract_schema(db):
    try:
        inspector = inspect(db.bind)
        schema_str = ""
        
        for table_name in inspector.get_table_names():
            schema_str += f"Table {table_name}:\n"
            columns = inspector.get_columns(table_name)
            for column in columns:
                schema_str += f"  - {column['name']} ({column['type']})\n"
        
        return schema_str

    except Exception as e:
        schema_logger.error(f"Schema extraction failed: {e}")
        raise
