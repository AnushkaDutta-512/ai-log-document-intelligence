from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.embeddings import generate_embeddings
from backend.vector_store.faiss_store import store

router = APIRouter(prefix="/store", tags=["Store"])

class StoreRequest(BaseModel):
    filename: str
    chunks: List[str]
    source: str  # e.g., 'pdf', 'txt', 'log'

class StoreResponse(BaseModel):
    message: str
    chunks_stored: int

@router.post("/", response_model=StoreResponse)
async def store_embeddings(request: StoreRequest):
    """Generates embeddings for chunks and stores them in FAISS."""
    if not request.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")
        
    # Generate embeddings (we need the actual vectors here)
    num_chunks, dim, embeddings = generate_embeddings(request.chunks)
    
    # Prepare metadata 
    metadatas = [
        {"text": chunk, "source": request.source, "filename": request.filename}
        for chunk in request.chunks
    ]
    
    # Store in FAISS
    try:
        stored_count = store.add_embeddings(embeddings, metadatas)
        store.save() # Persist to disk
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing embeddings: {str(e)}")
        
    return StoreResponse(
        message="Embeddings successfully stored",
        chunks_stored=stored_count
    )

@router.get("/files")
async def list_files():
    """Returns a list of all unique files currently in the vector store."""
    filenames = store.get_all_filenames()
    return {"files": filenames}

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Deletes all chunks belonging to a specific filename from the vector store."""
    deleted = store.delete_by_filename(filename)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="File not found in vector store")
    return {"message": f"Successfully deleted {deleted} chunks for {filename}", "deleted": deleted}
