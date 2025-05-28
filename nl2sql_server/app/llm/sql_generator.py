import openai
from loguru import logger
from llm.prompt_examples import FEW_SHOT_SQL_EXAMPLES

llm_logger = logger.bind(llm=True)

async def generate_sql(question: str, schema: str, api_key: str, return_usage: bool = False):
    prompt = f"""
You are a PostgreSQL SQL expert. Given the following database schema and natural language question,
generate a correct and complete SQL query.

Follow these strict rules:
- No comments, explanations, or extra formatting.
- SQL must be valid PostgreSQL.
- Use table and column names exactly as given.
- Fully qualify ambiguous columns if needed.
- WHERE, JOIN, GROUP BY, and ORDER BY clauses must be explicit if needed.
- Do not use aliases in WHERE or HAVING clauses.
- Do not use window functions in invalid places (e.g., HAVING).
- Always complete the query even if conditions are complex.
- Output must be SQL only.

Note: PostgreSQL does not support INTERVAL '1 quarter'. Use INTERVAL '3 months' instead for quarters.

Here are examples of incorrect vs correct SQL (for learning):

{FEW_SHOT_SQL_EXAMPLES}

Schema:
{schema}

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

        sql_output = response.choices[0].message.content.strip()
        usage = response.usage  # Contains prompt_tokens, completion_tokens, total_tokens

        if return_usage:
            return {
                "sql": sql_output,
                "token_usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
        else:
            return sql_output

    except openai.APIError as e:
        llm_logger.error(f"OpenAI API error: {e} | Prompt: {question}")
        return {"status": "error", "message": "OpenAI API error"}
    except Exception as e:
        llm_logger.error(f"Unexpected error: {e} | Prompt: {question}")
        return {"status": "error", "message": str(e)}
