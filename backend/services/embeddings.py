from sentence_transformers import SentenceTransformer


# Load once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generate embeddings locally using SentenceTransformers.
    No API key required.
    """
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.tolist()
