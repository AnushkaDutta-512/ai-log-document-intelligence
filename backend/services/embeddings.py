from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import numpy as np
from backend.config import config

# -----------------------------
# Load Model Once (Global)
# -----------------------------
MODEL_NAME = config.MODEL_NAME
model = SentenceTransformer(MODEL_NAME)


# -----------------------------
# Generate Embeddings
# -----------------------------
def generate_embeddings(chunks: List[str]) -> Tuple[int, int, np.ndarray]:
    """
    Generates embeddings for given chunks.

    Returns:
        - number of chunks
        - embedding dimension
        - embeddings (numpy array)
    """
    if not chunks:
        return 0, 0, np.array([])

    embeddings = model.encode(chunks, convert_to_numpy=True)

    num_chunks = embeddings.shape[0]
    dim = embeddings.shape[1]

    return num_chunks, dim, embeddings


# -----------------------------
# Encode Query
# -----------------------------
def encode_query(query: str) -> np.ndarray:
    """Encodes a query string into embedding."""
    return model.encode([query], convert_to_numpy=True)


# -----------------------------
# Get Model (optional utility)
# -----------------------------
def get_model() -> SentenceTransformer:
    """Returns the loaded embedding model."""
    return model