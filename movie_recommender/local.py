import json
from src.retrieval import find_similar_movies
from src.story_generation import generate_story
from src.embedding import save_embeddings, generate_embeddings

with open("datasets/movies.json", "r") as file:
    movies_data = json.load(file)

to_embed = [f"{movie.get('title', '')} {movie.get('overview', '')} {movie.get('tagline', '')}".strip() for movie in movies_data]
embeddings = generate_embeddings(to_embed)

# to save embeddings in local file 
# save_embeddings(embeddings)

query = "super hero action movie with a timeline twist"
top_movies = find_similar_movies(query, to_embed, movies_data)
titles, overviews = zip(*top_movies)
story = generate_story(titles, overviews)
print(story)