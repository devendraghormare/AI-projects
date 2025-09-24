from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse
from llm.sql_generator import generate_sql
from db.schema_extractor.session import get_db
from db.schema_extractor.schema_extractor import extract_schema
from db.sql_executor.sql_executor import execute_query
from services.validator import validate_sql
from utils.formatter import format_results
from utils.optimizer import optimize_question
from utils.cache import get_cache, set_cache, make_hash_key
from core.config import settings
from loguru import logger  
import json  

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def generate_and_execute_query(request: QueryRequest):
    try:
        with get_db() as db:
            logger.info("DB connection established successfully.")

            # Extract schema
            schema_info = extract_schema(db)
            schema_str = json.dumps(schema_info, sort_keys=True) 
            logger.info(f"Schema info extracted: {schema_info}")

            # Optimize question
            optimized_question = optimize_question(request.question)
            logger.info(f"Optimized question: {optimized_question}")

            #  Check LLM cache
            cache_key_llm = make_hash_key(optimized_question + schema_str)
            cached_llm = get_cache(cache_key_llm)
            if cached_llm:
                logger.info("LLM result found in cache.")
                llm_result = json.loads(cached_llm)
            else:
                logger.info(f"Generating SQL for question: {optimized_question}")
                llm_result = await generate_sql(
                    optimized_question,
                    schema_info,
                    settings.OPENAI_API_KEY,
                    return_usage=True
                )
                set_cache(cache_key_llm, llm_result, expire=600)  

            sql_query = llm_result["sql"].replace('```sql', '').replace('```', '').strip()
            token_usage = llm_result.get("token_usage", {})
            logger.info(f"Generated SQL: {sql_query}")
            logger.info(f"Token usage: {token_usage}")

            # Validate SQL
            logger.info("Validating the SQL query.")
            is_valid = validate_sql(sql_query, allow_modifications=request.allow_modifications)
            if not is_valid:
                logger.error("Generated SQL is not safe to execute.")
                raise ValueError("Generated SQL is not safe to execute.")

            #  Check SELECT result cache
            if sql_query.lower().strip().startswith("select"):
                cache_key_result = make_hash_key(sql_query)
                cached_result = get_cache(cache_key_result)
                if cached_result:
                    logger.info("Query result found in cache.")
                    formatted_results = json.loads(cached_result)
                else:
                    logger.info("Executing the SQL query.")
                    rows, columns = execute_query(db, sql_query)
                    logger.info(f"Query executed successfully, fetched {len(rows)} rows.")
                    formatted_results = format_results(rows, columns)
                    set_cache(cache_key_result, formatted_results, expire=300)  # 5 minutes
            else:
                logger.info("Executing non-SELECT SQL query.")
                rows, columns = execute_query(db, sql_query)
                logger.info(f"Query executed successfully, fetched {len(rows)} rows.")
                formatted_results = format_results(rows, columns)

            return QueryResponse(
                sql_query=sql_query,
                table=formatted_results["table"],
                results=formatted_results["json"],
                token_usage=token_usage
            )

    except Exception as e:
        logger.error(f"Error during query generation and execution: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
