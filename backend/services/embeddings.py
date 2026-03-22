from sentence_transformers import SentenceTransformer
<<<<<<< HEAD
from typing import List, Tuple
import numpy as np
from backend.config import config
=======
from backend.vector_store.faiss_store import FAISSStore

_model = None
>>>>>>> 02b64a9c6e824b60744c91a3c174793b3fbe4992

# Load the local model specified in the prompt
MODEL_NAME = config.MODEL_NAME
model = SentenceTransformer(MODEL_NAME)

<<<<<<< HEAD
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
=======
def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generate_embeddings(chunks: list[str], source: str = "unknown") -> list[list[float]]:
    """
    Generate embeddings and persist to FAISS with source metadata.
    """
    model = get_model()
    embeddings = model.encode(chunks, convert_to_numpy=True)
    embeddings_list = embeddings.tolist()

    if embeddings_list:
        store = FAISSStore(dimension=len(embeddings_list[0]))
        metadata = [{"text": chunk, "source": source, "chunk_id": i} for i, chunk in enumerate(chunks)]
        store.add_embeddings(embeddings_list, metadata)
        store.save()

    return embeddings_list
>>>>>>> 02b64a9c6e824b60744c91a3c174793b3fbe4992
