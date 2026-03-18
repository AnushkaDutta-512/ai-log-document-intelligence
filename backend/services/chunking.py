import re
from typing import List
from backend.config import config

def chunk_text(text: str, filename: str) -> List[str]:
    """Chunks text based on file type."""
    ext = filename.lower().split(".")[-1]
    
    if ext == "log":
        # Chunk logs by lines
        lines = text.split("\n")
        # To avoid tiny chunks, we could group every 10 lines
        # but the prompt says "logs -> line-based"
        # Let's chunk every 10 lines to give it some context
        chunks = []
        current_chunk = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            current_chunk.append(line)
            if len(current_chunk) >= 5: # Small chunks for logs
                chunks.append("\n".join(current_chunk))
                current_chunk = []
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return chunks
        
    elif ext in ["pdf", "txt"]:
        # Chunk by paragraph
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = [p.strip() for p in paragraphs if p.strip()]
        
        # Fallback if there are no paragraphs (just one huge text block)
        if len(chunks) == 1 and len(text) > 2000:
            return _character_chunk(text)
            
        return chunks
        
    else:
        # Fallback
        return _character_chunk(text)

def _character_chunk(text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
