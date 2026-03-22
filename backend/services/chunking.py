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

<<<<<<< HEAD
def _character_chunk(text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> List[str]:
=======
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    file_type: str = "default"
) -> List[str]:
    """
    Smart chunking based on file type:
    - logs: line-based chunking
    - pdf/txt: paragraph-based chunking
    - default: character-based chunking with overlap
    """
    if file_type == "log":
        return _chunk_by_lines(text)
    elif file_type in ["pdf", "txt"]:
        return _chunk_by_paragraphs(text, chunk_size, overlap)
    else:
        return _chunk_by_characters(text, chunk_size, overlap)


def _chunk_by_lines(text: str, lines_per_chunk: int = 20) -> List[str]:
    """For log files — group lines into chunks."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    chunks = []
    for i in range(0, len(lines), lines_per_chunk):
        chunk = "\n".join(lines[i:i + lines_per_chunk])
        chunks.append(chunk)
    return chunks


def _chunk_by_paragraphs(text: str, chunk_size: int, overlap: int) -> List[str]:
    """For PDFs/TXT — split by paragraphs, merge small ones."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) <= chunk_size:
            current += "\n\n" + para if current else para
        else:
            if current:
                chunks.append(current)
            # If single paragraph exceeds chunk_size, split it further
            if len(para) > chunk_size:
                sub_chunks = _chunk_by_characters(para, chunk_size, overlap)
                chunks.extend(sub_chunks[:-1])
                current = sub_chunks[-1] if sub_chunks else ""
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def _chunk_by_characters(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Fallback: fixed-size character chunks with overlap."""
>>>>>>> 02b64a9c6e824b60744c91a3c174793b3fbe4992
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
<<<<<<< HEAD
        start += chunk_size - overlap
    return chunks
=======
        start = end - overlap
        if start < 0:
            start = 0

    return chunks
>>>>>>> 02b64a9c6e824b60744c91a3c174793b3fbe4992
