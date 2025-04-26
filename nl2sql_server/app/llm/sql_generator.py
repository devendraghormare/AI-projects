import openai

# Async function to generate SQL
async def generate_sql(question: str, schema: str, api_key: str) -> str:
    prompt = f"""Given the following database schema:

{schema}

Write a SQL query to answer the following question: "{question}". 
Return only the SQL code without any explanation or extra text.
"""

    try:
        # Create OpenAI Async client dynamically with passed api_key
        client = openai.AsyncOpenAI(api_key=api_key)

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes SQL queries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=150,
        )

        sql_query = response.choices[0].message.content.strip()
        return sql_query

    except openai.APIError as e:
        print(f"OpenAI API error: {e}")
        return "Error: Unable to generate SQL query due to an API issue."
    except Exception as e:
        print(f"Error during query generation: {e}")
        return f"Error: {str(e)}"
