import openai
from loguru import logger

llm_logger = logger.bind(llm=True)

async def generate_sql(question: str, schema: str, api_key: str, return_usage: bool = False):
    # Base optimized prompt
    prompt = f"""
You are a PostgreSQL SQL expert. Given a database schema and a natural language question, generate a valid SQL query.

Rules:
- Output only the SQL query (no markdown, comments, or explanations).
- Use correct PostgreSQL syntax.
- Use exact table and column names as given in the schema.
- Qualify ambiguous column names if needed.
- Do not use aliases in WHERE or HAVING clauses.
- Do not use window functions in HAVING or WHERE.
- Use explicit JOINs, GROUP BYs, and ORDER BYs when needed.
- PostgreSQL does not support INTERVAL '1 quarter' — use INTERVAL '3 months' instead.

Schema:
{schema}

Question: "{question}"
"""

    # Optional few-shot example added only if needed (dynamic optimization)
    if any(keyword in question.lower() for keyword in ["trend", "over time", "monthly average", "improve"]):
        prompt += """
        
Example (monthly rating trend check):

WITH monthly_aggregates AS (
    SELECT product_id, DATE_TRUNC('month', created_at) AS month, AVG(rating) AS avg_rating
    FROM reviews
    GROUP BY product_id, month
),
with_lag AS (
    SELECT *, LAG(avg_rating) OVER (PARTITION BY product_id ORDER BY month) AS prev_avg_rating
    FROM monthly_aggregates
)
SELECT *
FROM with_lag
WHERE avg_rating > prev_avg_rating;
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
        usage = response.usage

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
