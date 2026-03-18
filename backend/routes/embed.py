from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.embeddings import generate_embeddings

router = APIRouter(prefix="/embed", tags=["Embed"])

class EmbedRequest(BaseModel):
    chunks: List[str]

class EmbedResponse(BaseModel):
    chunk_count: int
    embedding_dimension: int

@router.post("/", response_model=EmbedResponse)
async def embed_chunks(request: EmbedRequest):
    """Generates embeddings for a list of text chunks."""
    if not request.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")
        
    num_chunks, dim, _ = generate_embeddings(request.chunks)
    
    return EmbedResponse(
        chunk_count=num_chunks,
        embedding_dimension=dim
    )
