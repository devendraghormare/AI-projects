from together import Together
import numpy as np
import pickle
from typing import List
from src.config import TOGETHER_API_KEY, EMBEDDING_MODEL

def generate_embeddings(input_texts: List[str]) -> List[List[float]]:
    together_client = Together(api_key=TOGETHER_API_KEY)
    outputs = together_client.embeddings.create(
        input=input_texts,
        model=EMBEDDING_MODEL,
    )
    return np.array([x.embedding for x in outputs.data])


def save_embeddings(embeddings: List[List[float]], file_path: str = "embeddings/vector_store.pkl"):
    with open(file_path, "wb") as f:
        pickle.dump(embeddings, f)
    
