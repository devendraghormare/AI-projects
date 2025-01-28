import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.embedding import generate_embeddings
from typing import List

def find_similar_movies(query: str, movie_texts: List[str], movies_data: List[dict], top_n=10):
    query_embedding = generate_embeddings([query])[0]
    embeddings = generate_embeddings(movie_texts)
    similarity_scores = cosine_similarity([query_embedding], embeddings)
    indices = np.argsort(-similarity_scores[0])[:top_n]
    return [(movies_data[i]["title"], movies_data[i]["overview"]) for i in indices]