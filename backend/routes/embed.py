from fastapi import APIRouter, HTTPException
from backend.services.text_extraction import extract_text_from_file
from backend.services.chunking import chunk_text
from backend.services.embeddings import generate_embeddings
from backend.vector_store.faiss_store import FAISSStore
from sentence_transformers import SentenceTransformer

router = APIRouter()

model = SentenceTransformer("all-MiniLM-L6-v2")


@router.get("/embed")
def embed_document(file_path: str):
    try:
        text = extract_text_from_file(file_path)
        chunks = chunk_text(text)
        embeddings = generate_embeddings(chunks)

        return {
            "file_path": file_path,
            "total_chunks": len(chunks),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
def query_documents(question: str, k: int = 5):
    try:
        query_embedding = model.encode(question).tolist()

        store = FAISSStore(dimension=len(query_embedding))

        results = store.search(query_embedding, k)

        return {
            "question": question,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))