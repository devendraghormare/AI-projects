import logging
from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse
from llm.sql_generator import generate_sql
from db.schema_extractor.session import get_db
from db.schema_extractor.schema_extractor import extract_schema
from db.sql_executor.sql_executor import execute_query
from services.validator import validate_sql
from utils.formatter import format_results
from utils.optimizer import optimize_question
from core.config import settings

# Set up logging to file
log_file = "./logs/query_execution.log"  
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        # logging.StreamHandler()  
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def generate_and_execute_query(request: QueryRequest):
    try:
        with get_db() as db:
            logger.info("DB connection established successfully.")
            schema_info = extract_schema(db)
            logger.info(f"Schema info extracted: {schema_info}")

            optimized_question = optimize_question(request.question)
            logger.info(f"Optimized question: {optimized_question}")

            # Generate SQL query
            logger.info(f"Generating SQL for question: {optimized_question}")
            sql_query = await generate_sql(optimized_question, schema_info, settings.OPENAI_API_KEY)

            # Remove markdown formatting (backticks and "sql" tag)
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()

            logger.info(f"Generated SQL: {sql_query}")

            # Validate the SQL query
            logger.info("Validating the SQL query.")
            is_valid = validate_sql(sql_query, allow_modifications=request.allow_modifications)
            if not is_valid:
                logger.error("Generated SQL is not safe to execute.")
                raise ValueError("Generated SQL is not safe to execute.")

            # Execute the SQL query
            logger.info("Executing the SQL query.")
            rows, columns = execute_query(db, sql_query)
            logger.info(f"Query executed successfully, fetched {len(rows)} rows.")

            formatted_results = format_results(rows, columns)
            logger.info(f"Formatted the results: {formatted_results}")

            # Return full response
            return QueryResponse(
                sql_query=sql_query,
                table=formatted_results["table"], 
                results=formatted_results["json"]
            )

    except Exception as e:
        logger.error(f"Error during query generation and execution: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
