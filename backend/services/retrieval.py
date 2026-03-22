import logging
from typing import List, Dict, Any, Optional

from backend.services.embeddings import encode_query
from backend.vector_store.faiss_store import store

from sentence_transformers import CrossEncoder

logging.basicConfig(level=logging.INFO)

# 🔥 Load cross-encoder (for re-ranking)
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


# -----------------------------
# 🔥 Re-ranking Function
# -----------------------------
def rerank_results(query: str, results: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    """
    Re-rank retrieved chunks using cross-encoder.
    """

    if not results:
        return results

    logging.info("Starting re-ranking step")

    pairs = [(query, r["text"]) for r in results]

    scores = cross_encoder.predict(pairs)

    for i, r in enumerate(results):
        r["rerank_score"] = float(scores[i])

    # Sort by rerank score (descending)
    results = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    logging.info("Re-ranking completed")

    return results[:top_k]


# -----------------------------
# 🔥 Main Retrieval Function
# -----------------------------
def retrieve_context(
    query: str,
    k: int = 5,
    source_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves top-k relevant chunks using:
    1. FAISS (semantic search)
    2. Cross-encoder (re-ranking)
    """

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if k <= 0:
        raise ValueError("k must be greater than 0")

    logging.info(f"Retrieval started for query: {query}")
    logging.info(f"Top-K: {k}, Source filter: {source_filter}")

    # -----------------------------
    # Step 1: Encode query
    # -----------------------------
    query_embedding = encode_query(query)

    # -----------------------------
    # Step 2: FAISS search (get more for reranking)
    # -----------------------------
    initial_k = k * 3  # 🔥 fetch more candidates

    raw_results = store.search(
        query_embedding,
        k=initial_k,
        source_filter=source_filter
    )

    if not raw_results:
        return []

    # -----------------------------
    # Step 3: Format results
    # -----------------------------
    formatted_results = []

    for i, result in enumerate(raw_results):
        formatted_results.append({
    "rank": int(i + 1),
    "text": result.get("text", ""),
    "score": float(result.get("score", 0.0)),
    "source": result.get("source", "unknown"),
    "chunk_id": int(result.get("chunk_id", -1))
})

    # -----------------------------
    # Step 4: 🔥 Re-rank results
    # -----------------------------
    reranked_results = rerank_results(query, formatted_results, k)

    logging.info(f"Retrieved {len(reranked_results)} final results")

    return reranked_results