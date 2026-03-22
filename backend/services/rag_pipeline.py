from backend.services.retrieval import retrieve_context
from pydantic import BaseModel
from typing import Optional, List, Dict
from backend.config import config
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

# Configure Gemini if API key exists
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)


# -----------------------------
# Request / Response Models
# -----------------------------
class QueryRequest(BaseModel):
    query: str
    k: int = 8
    source_filter: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Dict]


# -----------------------------
# RAG Pipeline
# -----------------------------
def generate_rag_response(
    query: str,
    k: int = 10,
    source_filter: Optional[str] = None
) -> QueryResponse:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks
    2. Build context
    3. Generate answer using LLM (Gemini) or fallback
    """

    if not query.strip():
        raise ValueError("Query cannot be empty")

    logging.info(f"RAG query: {query}")

    # -----------------------------
    # Step 1: Retrieve context
    # -----------------------------
    context_chunks = retrieve_context(query, k, source_filter)

    if not context_chunks:
        logging.warning("No relevant context found")
        return QueryResponse(
            query=query,
            answer="No relevant information found in the uploaded documents.",
            sources=[]
        )

    # -----------------------------
    # Step 2: Build context
    # -----------------------------
    context_text = "\n\n".join([
        f"[Chunk {i+1}]: {chunk['text']}"
        for i, chunk in enumerate(context_chunks)
    ])

    # Limit context size
    context_text = context_text[:4000]

    logging.info(f"Retrieved {len(context_chunks)} chunks")
    logging.info(f"Context length: {len(context_text)} characters")

    # -----------------------------
    # Step 3: Generate answer
    # -----------------------------
    if config.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""
You are an intelligent AI assistant.

Your task is to:
- Analyze multiple pieces of context
- Combine information from different parts
- Perform reasoning across documents
- Give a clear, final answer

Instructions:
- Connect related ideas across chunks
- Do NOT just repeat text
- Synthesize information into one answer
- If multiple sources contribute, combine them logically
- If answer is not found, say "Not found in provided documents"

Context:
{context_text}

Question:
{query}
"""

            response = model.generate_content(prompt)

            answer = response.text.strip() if response.text else "No response generated."

            if not answer:
                answer = "Could not generate a meaningful response."

        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            answer = "Error generating response from LLM."

    else:
        logging.info("Using fallback (no API key)")

        answer = f"Based on retrieved context:\n\n{context_text[:500]}"

    # -----------------------------
    # Step 4: Clean & Deduplicate Sources
    # -----------------------------
    seen = set()
    sources = []

    for c in context_chunks:
        key = (c.get("source"), c.get("chunk_id"))
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": c.get("source"),
                "chunk_id": c.get("chunk_id"),
                "score": c.get("score")
            })

    return QueryResponse(
        query=query,
        answer=answer,
        sources=sources
    )