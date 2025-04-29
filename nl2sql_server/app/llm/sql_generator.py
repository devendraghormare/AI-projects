import openai
from loguru import logger
# from prompt_examples import FEW_SHOT_SQL_EXAMPLES


llm_logger = logger.bind(llm=True)

FEW_SHOT_SQL_EXAMPLES = """
Example 1:
Question: Find products where average rating improved over time (e.g., monthly average rating is increasing).

❌ Incorrect SQL (fails due to use of window function in HAVING clause):
SELECT 
    products.product_id, 
    products.name, 
    AVG(reviews.rating) AS average_rating, 
    DATE_TRUNC('month', reviews.created_at) AS month
FROM 
    products
JOIN 
    reviews ON products.product_id = reviews.product_id
GROUP BY 
    products.product_id, 
    products.name, 
    DATE_TRUNC('month', reviews.created_at)
HAVING 
    AVG(reviews.rating) > LAG(AVG(reviews.rating)) OVER (PARTITION BY products.product_id ORDER BY DATE_TRUNC('month', reviews.created_at))
ORDER BY 
    products.product_id, 
    DATE_TRUNC('month', reviews.created_at);

❗ Problem: Window functions like `LAG()` are not allowed in the HAVING clause in PostgreSQL.

✅ Correct SQL:
WITH monthly_aggregates AS (
    SELECT product_id, DATE_TRUNC('month', created_at) AS month, AVG(rating) AS avg_rating
    FROM reviews
    GROUP BY product_id, month
),
with_lag AS (
    SELECT *,
           LAG(avg_rating) OVER (PARTITION BY product_id ORDER BY month) AS prev_avg_rating
    FROM monthly_aggregates
)
SELECT *
FROM with_lag
WHERE avg_rating > prev_avg_rating;
"""


async def generate_sql(question: str, schema: str, api_key: str) -> str:
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
        return response.choices[0].message.content.strip()

    except openai.APIError as e:
        llm_logger.error(f"OpenAI API error: {e} | Prompt: {question}")
        return {"status": "error", "message": "OpenAI API error"}
    except Exception as e:
        llm_logger.error(f"Unexpected error: {e} | Prompt: {question}")
        return {"status": "error", "message": str(e)}
