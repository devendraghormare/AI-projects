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
from loguru import logger  

# Router setup
router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def generate_and_execute_query(request: QueryRequest):
    try:
        # Start DB connection
        with get_db() as db:
            logger.info("DB connection established successfully.")

            # Extract schema info
            schema_info = extract_schema(db)
            logger.info(f"Schema info extracted: {schema_info}")

            # Optimize question
            optimized_question = optimize_question(request.question)
            logger.info(f"Optimized question: {optimized_question}")

            # Generate SQL query from LLM and get token usage
            logger.info(f"Generating SQL for question: {optimized_question}")
            llm_result = await generate_sql(
                optimized_question,
                schema_info,
                settings.OPENAI_API_KEY,
                return_usage=True
            )
            sql_query = llm_result["sql"]
            token_usage = llm_result.get("token_usage", {})

            # Clean up the SQL query (remove markdown if any)
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            logger.info(f"Generated SQL: {sql_query}")
            logger.info(f"Token usage: {token_usage}")

            # Validate SQL query
            logger.info("Validating the SQL query.")
            is_valid = validate_sql(sql_query, allow_modifications=request.allow_modifications)
            if not is_valid:
                logger.error("Generated SQL is not safe to execute.")
                raise ValueError("Generated SQL is not safe to execute.")

            # Execute the SQL query
            logger.info("Executing the SQL query.")
            rows, columns = execute_query(db, sql_query)
            logger.info(f"Query executed successfully, fetched {len(rows)} rows.")

            # Format and return results
            formatted_results = format_results(rows, columns)
            logger.info("Formatted the results.")

            return QueryResponse(
                sql_query=sql_query,
                table=formatted_results["table"],
                results=formatted_results["json"],
                token_usage=token_usage  # Include this in response
            )

    except Exception as e:
        logger.error(f"Error during query generation and execution: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
