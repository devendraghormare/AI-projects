import openai
from loguru import logger
from prompt_examples import FEW_SHOT_SQL_EXAMPLES


llm_logger = logger.bind(llm=True)

async def generate_sql(question: str, schema: str, api_key: str) -> str:
    prompt = f"""
        Given the following database schema:

        {schema}

        You must generate only the SQL query based on the schema and question.
        Follow these strict rules:
        - No comments, explanations, or extra formatting.
        - SQL must be valid PostgreSQL.
        - Use table and column names exactly as given.
        - Fully qualify ambiguous columns if needed.
        - WHERE, JOIN, GROUP BY, and ORDER BY clauses must be explicit if needed.
        - Do not use aliases in WHERE or HAVING clauses.
        - Always complete the query even if conditions are complex.
        - Output must start and end with SQL only.

        Here are examples of incorrect vs correct SQL (for learning):

        {FEW_SHOT_SQL_EXAMPLES}

        Question: "{question}"
    """

    try:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes SQL queries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=250,
            timeout=30.0
        )
        return response.choices[0].message.content.strip()

    except openai.APIError as e:
        llm_logger.error(f"OpenAI API error: {e} | Prompt: {question}")
        return {"status": "error", "message": "OpenAI API error"}
    except Exception as e:
        llm_logger.error(f"Unexpected error: {e} | Prompt: {question}")
        return {"status": "error", "message": str(e)}
