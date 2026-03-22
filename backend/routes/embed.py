from fastapi import APIRouter, HTTPException

from pydantic import BaseModel
from typing import List
from backend.services.embeddings import generate_embeddings, get_model
from backend.services.text_extraction import extract_text_from_file
from backend.services.chunking import chunk_text
from backend.vector_store.faiss_store import FAISSStore


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

@router.get("/embed")
def embed_document(file_path: str):
    try:
        text = extract_text_from_file(file_path)

        # Detect file type from extension
        extension = file_path.rsplit(".", 1)[-1].lower()
        file_type = extension if extension in ["pdf", "txt", "log"] else "default"
        chunks = chunk_text(text, file_path)
        embeddings = generate_embeddings(chunks, source=file_path)

        return {
            "file_path": file_path,
            "file_type": file_type,
            "total_chunks": len(chunks),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
def query_documents(question: str, k: int = 5, source: str = None):
    try:
        model = get_model()
        query_embedding = model.encode(question).tolist()

        store = FAISSStore(dimension=len(query_embedding))
        results = store.search(query_embedding, k, source_filter=source)

        if not results:
            return {
                "question": question,
                "answer": "No relevant context found. Please upload and embed a document first.",
                "retrieved_chunks": [],
                "chunks_returned": 0
            }

        top_chunks = results[:3]
        context = "\n\n".join([r["text"] for r in top_chunks])
        answer = f"Based on the document context:\n\n{context[:600]}"

        for r in results:
            score = r["score"]
            if score < 0.3:
                r["confidence"] = "high"
            elif score < 0.6:
                r["confidence"] = "medium"
            else:
                r["confidence"] = "low"

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": results,
            "chunks_returned": len(results)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
