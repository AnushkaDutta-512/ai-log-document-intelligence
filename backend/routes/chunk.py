from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.chunking import chunk_text

router = APIRouter(prefix="/chunk", tags=["Chunk"])

class ChunkRequest(BaseModel):
    text: str
    filename: str

class ChunkResponse(BaseModel):
    filename: str
    chunk_count: int
    chunks: List[str]

@router.post("/", response_model=ChunkResponse)
async def create_chunks(request: ChunkRequest):
    """Chunks text into smaller pieces."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")
        
    chunks = chunk_text(request.text, request.filename)
    
    return ChunkResponse(
        filename=request.filename,
        chunk_count=len(chunks),
        chunks=chunks
    )
