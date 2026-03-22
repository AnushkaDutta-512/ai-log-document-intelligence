from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from backend.services.embeddings import generate_embeddings
from backend.vector_store.faiss_store import store

router = APIRouter(prefix="/store", tags=["Store"])


class StoreRequest(BaseModel):
    filename: str
    chunks: List[str]
    source: str


class StoreResponse(BaseModel):
    message: str
    chunks_stored: int


# -----------------------------
# Store embeddings
# -----------------------------
@router.post("/", response_model=StoreResponse)
async def store_embeddings(request: StoreRequest):
    if not request.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")

    try:
        num_chunks, dim, embeddings = generate_embeddings(request.chunks)

        metadatas = [
            {
                "text": chunk,
                "source": request.source,
                "filename": request.filename,
                "chunk_id": i
            }
            for i, chunk in enumerate(request.chunks)
        ]

        stored_count = store.add_embeddings(embeddings, metadatas)
        store.save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return StoreResponse(
        message="Embeddings successfully stored",
        chunks_stored=stored_count
    )


# -----------------------------
# List files
# -----------------------------
@router.get("/files")
async def list_files():
    try:
        filenames = store.get_all_filenames()
        return {"files": filenames}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Delete file
# -----------------------------
@router.delete("/files/{filename}")
async def delete_file(filename: str):
    deleted = store.delete_by_filename(filename)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "message": f"Deleted {deleted} chunks for {filename}",
        "deleted": deleted
    }