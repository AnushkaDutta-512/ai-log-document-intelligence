from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import numpy as np
from backend.config import config

# Load the local model specified in the prompt
MODEL_NAME = config.MODEL_NAME
model = SentenceTransformer(MODEL_NAME)

def generate_embeddings(chunks: List[str]) -> Tuple[int, int, np.ndarray]:
    """
    Generates embeddings for given chunks.
    Returns:
        - chunk count
        - embedding dimension
        - vectors (numpy array)
    Note: The prompt says "Return only: chunk count, embedding dimension"
    for the `/embed` endpoint, but we need the actual vectors to store in FAISS.
    So this service returns all three, and the route will filter the response.
    """
    if not chunks:
        return 0, 0, np.array([])
        
    embeddings = model.encode(chunks, convert_to_numpy=True)
    num_chunks = embeddings.shape[0]
    dim = embeddings.shape[1]
    
    return num_chunks, dim, embeddings

def encode_query(query: str) -> np.ndarray:
    """Encodes a single query string for search."""
    return model.encode([query], convert_to_numpy=True)
