from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.services.retrieval import retrieve_context

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    source_filter: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]

@router.post("/", response_model=SearchResponse)
async def search_index(request: SearchRequest):
    """Searches the vector store for top chunks matching the query."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        results = retrieve_context(request.query, request.k, request.source_filter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
        
    return SearchResponse(
        query=request.query,
        results=results
    )
