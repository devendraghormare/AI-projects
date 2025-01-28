from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from together import Together
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize Together API client
together_api_key = os.getenv('TOGETHER_API_KEY')
client = Together(api_key=together_api_key)

# Define the model to handle the input format
class QueryRequest(BaseModel):
    question: str

class LLMResponse(BaseModel):
    response: str

def chat_with_together(client, prompt, model):
    response = client.completions.create(
        model=model,
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )

    if isinstance(response, str):
        return response.strip()
    else:
        return response.choices[0].text.strip()

def extract_sql_query(llm_response: str) -> str:
    """
    Extracts the SQL query from the LLM response.

    Args:
        llm_response: The raw LLM response string.

    Returns:
        The extracted SQL query as a string or an empty string if no SQL is found.
    """
    # Regular expression to match the SQL part inside the JSON block
    sql_pattern = r'"sql":\s*"([^"]+)"'
    
    # Search for the pattern and return the first match if found
    match = re.search(sql_pattern, llm_response)
    
    if match:
        return match.group(1)  # Return only the SQL query part
    return ""  # Return an empty string if no match is found

# Define the FastAPI endpoint
@app.post("/generate-sql", response_model=LLMResponse)
async def generate_sql(query_request: QueryRequest):
    user_question = query_request.question

    model = "meta-llama/Meta-Llama-3-8B-Instruct-Turbo"

    # Load the base prompt (replace with your actual path or base prompt)
    with open('prompts/base_prompt.txt', 'r') as file:
        base_prompt = file.read()

    # Generate the full prompt for the AI
    full_prompt = base_prompt.format(user_question=user_question)

    # Get the AI's response from Together
    llm_response = chat_with_together(client, full_prompt, model)

    print("This is the LLM response:", llm_response)

    # Extract the SQL query from the response
    sql_query = extract_sql_query(llm_response)

    if sql_query:
        # Return the cleaned SQL query as a response
        return LLMResponse(response=sql_query)
    else:
        raise HTTPException(status_code=400, detail="Could not extract SQL query from the response.")


