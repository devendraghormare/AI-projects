import streamlit as st
import requests

# FastAPI URL (assuming FastAPI app is running locally on port 8000)
fastapi_url = "http://127.0.0.1:8000/generate_story"

def get_story_from_fastapi(query: str):
    response = requests.get(fastapi_url, params={"query": query})
    if response.status_code == 200:
        return response.json()["story"]
    else:
        return "Error fetching story."

# Streamlit UI
st.title("Movie Story Generator")

query = st.text_input("Enter a movie genre or theme")

if query:
    story = get_story_from_fastapi(query)
    st.markdown(story, unsafe_allow_html=True)
