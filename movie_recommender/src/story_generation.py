from together import Together
from src.config import TOGETHER_API_KEY, LLM_MODEL
from typing import List

def generate_story(titles: List[str], overviews: List[str]) -> str:
    client = Together(api_key=TOGETHER_API_KEY)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a Pulitzer-winning storyteller."},
            {"role": "user", "content": f"Tell me a story about {titles}. Here is some information: {overviews}"},
        ],
    )
    return response.choices[0].message.content