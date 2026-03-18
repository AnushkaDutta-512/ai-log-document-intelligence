from backend.services.retrieval import retrieve_context
from pydantic import BaseModel
from typing import Optional
from backend.config import config
import google.generativeai as genai

if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)


class QueryRequest(BaseModel):
    query: str
    k: int = 5
    source_filter: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list

def generate_rag_response(query: str, k: int = 5, source_filter: Optional[str] = None) -> QueryResponse:
    """
    Simulates a RAG pipeline by retrieving context and 
    creating a naive response based on that context.
    """
    context_chunks = retrieve_context(query, k, source_filter)
    
    if not context_chunks:
        return QueryResponse(
            query=query,
            answer="I couldn't find any relevant context to answer your question.",
            sources=[]
        )
        
    # Combine retrieved texts
    context_text = "\n\n".join([chunk["text"] for chunk in context_chunks])
    
    if config.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"Answer the user's question precisely using ONLY the provided context.\n\nContext:\n{context_text}\n\nQuestion: {query}"
            resp = model.generate_content(prompt)
            answer = resp.text
        except Exception as e:
            answer = f"Error calling Gemini API: {str(e)}"
    else:
        answer = (
            "(This is a simulated LLM answer. To generate a real conversational response, "
            "please add a GEMINI_API_KEY to your .env file! Until then, please read the "
            "exact vector database excerpts above to find your answer.)"
        )
    
    return QueryResponse(
        query=query,
        answer=answer,
        sources=context_chunks
    )
