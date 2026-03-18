from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from backend.services.rag_pipeline import generate_rag_response

router = APIRouter(prefix="/query", tags=["Query"])

class QueryRequest(BaseModel):
    query: str
    k: int = 5
    source_filter: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict[str, Any]]

@router.post("/", response_model=QueryResponse)
async def perform_rag_query(request: QueryRequest):
    """Performs RAG by retrieving top chunks and simulating an LLM answer."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    try:
        response = generate_rag_response(request.query, request.k, request.source_filter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
        
    # Check if the returned object matches the expected response model
    # (The rag_pipeline service returns its own pydantic model for internal use)
    return QueryResponse(
        query=response.query,
        answer=response.answer,
        sources=response.sources
    )
