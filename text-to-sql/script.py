import os
import json
import sqlparse
from together import Together
from dotenv import load_dotenv

load_dotenv()


def chat_with_together(client, prompt, model):
    """
    Sends a prompt to the Together API and retrieves the response text.

    Args:
        client: The Together API client object.
        prompt: The prompt to send to the model.
        model: The name of the model to use for completion.

    Returns:
        The text response from the model.
    """
    response = client.completions.create(
        model=model,
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )

    # Access the text directly if it's a string, or from choices[0].text if it's a list
    if isinstance(response, str):
        return response.strip()
    else:
        return response.choices[0].text.strip()


def get_summarization(client, user_question, model):
    """
    Generates a summarization prompt and sends it to the Together API.

    Args:
        client: The Together API client object.
        user_question: The user's question.
        model: The name of the model to use for summarization.

    Returns:
        The AI's response to the summarization prompt.
    """
    prompt = f"""
    A user asked the following question:

    {user_question}

    In a few sentences, summarize the data or the query relevant to the question.
    """
    return chat_with_together(client, prompt, model)


# Use the Llama3 70b model or the most suitable Together AI model
model = "meta-llama/Meta-Llama-3-8B-Instruct-Turbo"

# Initialize Together API client
together_api_key = os.getenv('TOGETHER_API_KEY')
client = Together(api_key=together_api_key)

print("Welcome to the DuckDB Query Generator!")
print("You can ask questions about the data in the 'employees.csv' and 'purchases.csv' files.")

# Load the base prompt
with open('prompts/base_prompt.txt', 'r') as file:
    base_prompt = file.read()

while True:
    # Get the user's question
    user_question = input("Ask a question: ")

    if user_question:
        # Generate the full prompt for the AI
        full_prompt = base_prompt.format(user_question=user_question)

        # Get the AI's response from Together
        llm_response = chat_with_together(client, full_prompt, model)

        print(f"LLM Response: {llm_response}")  # Debug print statement

        try:
            # Attempt to parse as JSON first
            result_json = json.loads(llm_response)
        except json.decoder.JSONDecodeError:
            print("Warning: LLM response is not valid JSON. Attempting to process as plain text.")
            print("ERROR: Could not process LLM response.")  # No further processing in plain text case
            continue  # Skip to the next iteration

        # Process the response as JSON
        if 'sql' in result_json:
            sql_query = result_json['sql']
            formatted_sql_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
            print("```sql\n" + formatted_sql_query + "\n```")
        elif 'error' in result_json:
            print("ERROR:", 'Could not generate valid SQL for this question')
            print(result_json['error'])