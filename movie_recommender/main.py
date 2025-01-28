from fastapi import FastAPI, Query
import json
from src.retrieval import find_similar_movies
from src.story_generation import generate_story
from src.embedding import save_embeddings, generate_embeddings

app = FastAPI()

# Load movie dataset
with open("datasets/movies.json", "r") as file:
    movies_data = json.load(file)

# Generate embeddings
to_embed = [f"{movie.get('title', '')} {movie.get('overview', '')} {movie.get('tagline', '')}".strip() for movie in movies_data]
embeddings = generate_embeddings(to_embed)

# to save embeddings in local file 
# save_embeddings(embeddings)

@app.get("/generate_story")
def get_story(query: str = Query(..., title="Movie Query", description="Describe the type of movie story you want")):
    top_movies = find_similar_movies(query, to_embed, movies_data)
    titles, overviews = zip(*top_movies)
    story = generate_story(titles, overviews)

    # Replace '\n\n' with a line break
    story_with_line_breaks = story.replace("\n\n", "<br><br>")  # For HTML, or use '\n' for plain text
    return {"story": story_with_line_breaks}
