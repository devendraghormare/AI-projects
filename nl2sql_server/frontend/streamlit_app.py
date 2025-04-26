import streamlit as st
import requests
import pandas as pd

# Set up Streamlit page config
st.set_page_config(page_title="SQL Query Tester", layout="wide")

# Improved Dark Themed Custom CSS
st.markdown("""
    <style>
        /* Apply a nice font everywhere */
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }

        /* General background dark */
        .css-18e3th9 {
            background-color: #1e1e1e;
        }

        /* Sidebar background dark */
        section[data-testid="stSidebar"] {
            background-color: #2c2c2c;
            padding: 2rem 1rem;
            border-right: 2px solid #333333;
        }

        /* Sidebar titles */
        .css-1d391kg {
            font-size: 26px;
            font-weight: bold;
            color: #00C9A7;
            text-align: center;
            margin-bottom: 20px;
        }
        .css-1k85je5 {
            font-size: 16px;
            color: #cccccc;
            text-align: center;
            margin-bottom: 1rem;
        }

        /* Input Textbox */
        .stTextInput>div>div>input {
            padding: 12px 15px;
            font-size: 16px;
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 8px;
        }

        /* Buttons basic */
        .stButton>button {
            background-color: #00C9A7;
            color: #000000;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
            margin-top: 10px;
            width: 100%;
        }
        /* Buttons hover */
        .stButton>button:hover {
            background-color: #00b199;
            color: #ffffff;
        }

        /* DataFrame display */
        .stDataFrame {
            background-color: #2c2c2c;
            border: 1px solid #444444;
            border-radius: 10px;
            padding: 10px;
            color: #ffffff;
        }

        /* Spinner color */
        .stSpinner {
            color: #00C9A7;
        }

        /* Code block (SQL query) */
        .css-1c7y2kd {
            background-color: #2b2b2b;
            color: #00ffae;
            border-radius: 8px;
            padding: 10px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for input options
st.sidebar.title("SQL Query Tester")
st.sidebar.subheader("🧠 Provide a natural language question:")

# Input box for the user's natural language question
question = st.sidebar.text_input("Enter your question:")

# Allow the user to modify SQL or not
allow_modifications = st.sidebar.checkbox("Allow SQL Modifications")

# Button to clear the results
if st.sidebar.button("🧹 Clear Results"):
    st.session_state.results = None

# Header of the main content area
st.title(" SQL Query Generator & Executor")

# Loading spinner while waiting for API response
with st.spinner("Generating SQL query and fetching results..."):
    # Button to submit the query
    if st.sidebar.button("🔎 Submit Query"):
        if question:
            # Display the question
            st.write(f"### Question: '{question}'")

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

                    # Display the generated SQL
                    st.write(f"### 📝 Generated SQL Query:")
                    sql_query = data.get("sql_query", "")
                    if sql_query:
                        st.code(sql_query, language="sql")
                    else:
                        st.error("No SQL query generated.")

                    # Display the results in a data frame format
                    st.write(f"### 📊 Query Results:")

                    if "results" in data:
                        table_data = data["results"]
                        if isinstance(table_data, list):
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.error("Unexpected result format. Could not display as a table.")
                    else:
                        st.error("No results returned from the query.")
                else:
                    st.error(f"Error: {response.json()['detail']}")

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a question to generate the SQL query.")
    else:
        st.write("### 💬 SQL Query Tester")
        st.write("Use the sidebar to enter a natural language question and get the SQL query results.")
