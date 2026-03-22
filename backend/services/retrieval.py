import logging
from typing import List, Dict, Any, Optional

from backend.services.embeddings import encode_query
from backend.vector_store.faiss_store import store

logging.basicConfig(level=logging.INFO)


def retrieve_context(
    query: str,
    k: int = 5,
    source_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves top-k relevant chunks from FAISS vector store.

    Enhancements:
    - Logging for traceability
    - Input validation
    - Structured output with scores
    """

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if k <= 0:
        raise ValueError("k must be greater than 0")

    logging.info(f"Retrieval started for query: {query}")
    logging.info(f"Top-K: {k}, Source filter: {source_filter}")

    # Step 1: Encode query
    query_embedding = encode_query(query)

    # Step 2: Search vector store
    raw_results = store.search(
        query_embedding,
        k=k,
        source_filter=source_filter
    )

    # Step 3: Format results (VERY IMPORTANT)
    formatted_results = []

    for i, result in enumerate(raw_results):
        formatted_results.append({
            "rank": i + 1,
            "text": result.get("text", ""),
            "score": float(result.get("score", 0.0)),
            "source": result.get("metadata", {}).get("source", "unknown"),
            "chunk_id": result.get("metadata", {}).get("chunk_id", -1)
        })

    logging.info(f"Retrieved {len(formatted_results)} results")

    return formatted_results