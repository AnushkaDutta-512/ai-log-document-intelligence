from fastapi import APIRouter, HTTPException
from backend.services.text_extraction import extract_text_from_file
from backend.services.chunking import chunk_text
from backend.services.embeddings import generate_embeddings


router = APIRouter()


@router.get("/embed")
def embed_document(file_path: str):
    try:
        # Step 1: extract text
        text = extract_text_from_file(file_path)

        # Step 2: chunk text
        chunks = chunk_text(text)

        # Step 3: generate embeddings
        embeddings = generate_embeddings(chunks)

        return {
            "file_path": file_path,
            "total_chunks": len(chunks),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
