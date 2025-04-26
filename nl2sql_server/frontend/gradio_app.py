import gradio as gr
import requests
import pandas as pd

# Function to interact with the FastAPI backend
def generate_and_execute_query(question, allow_modifications):
    try:
        # API endpoint to generate and execute the query
        api_url = "http://localhost:8000/v1/query"  # Replace with your FastAPI endpoint
        headers = {"Content-Type": "application/json"}

        # Construct the request payload
        payload = {
            "question": question,
            "allow_modifications": allow_modifications
        }

        # Send the request to FastAPI backend
        response = requests.post(api_url, json=payload, headers=headers)

        # Handle successful responses
        if response.status_code == 200:
            data = response.json()

            sql_query = data.get("sql_query", "No SQL query generated.")
            results = data.get("results", [])

            # If results exist, format them into a DataFrame
            if results:
                df = pd.DataFrame(results)
                df.index = df.index + 1  # Indexing from 1
                table = df.to_html(classes="table table-bordered")  # Convert to HTML table for Gradio
            else:
                table = "No results returned from the query."

            return sql_query, table
        else:
            return "Error: " + response.json().get("detail", "Unknown error"), ""

    except Exception as e:
        return f"An error occurred: {e}", ""

# Build the Gradio interface
def build_gradio_interface():
    # Set up the Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("# SQL Query Generator & Executor")
        
        with gr.Row():
            question_input = gr.Textbox(label="Enter your question", placeholder="Ask a question like 'Find all products ordered by customer...'", lines=3)
            allow_modifications = gr.Checkbox(label="Allow SQL Modifications", value=False)
        
        with gr.Row():
            submit_button = gr.Button("Submit Query")
        
        sql_query_output = gr.Textbox(label="Generated SQL Query", interactive=False, lines=5)
        query_results_output = gr.HTML(label="Query Results")

        # Set up button action
        submit_button.click(
            generate_and_execute_query,
            inputs=[question_input, allow_modifications],
            outputs=[sql_query_output, query_results_output]
        )

    return demo

# Launch the interface
demo = build_gradio_interface()
demo.launch(share=True)  # `share=True` allows you to get a publicly accessible link
