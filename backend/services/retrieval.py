from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.services.embeddings import encode_query
from backend.vector_store.faiss_store import store

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    source_filter: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]

def retrieve_context(query: str, k: int = 5, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves relevant chunks from the FAISS store."""
    query_embedding = encode_query(query)
    results = store.search(query_embedding, k=k, source_filter=source_filter)
    return results
