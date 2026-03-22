import re
import logging
from typing import List
from backend.config import config

logging.basicConfig(level=logging.INFO)


def chunk_text(
    text: str,
    filename: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP
) -> List[str]:
    """
    Smart chunking based on file type:
    - logs → line-based chunking
    - pdf/txt → paragraph-based chunking
    - fallback → character-based chunking with overlap
    """

    if not text.strip():
        return []

    ext = filename.lower().split(".")[-1]

    logging.info(f"Chunking started for file type: {ext}")

    if ext == "log":
        chunks = _chunk_by_lines(text)

    elif ext in ["pdf", "txt"]:
        chunks = _chunk_by_paragraphs(text, chunk_size, overlap)

    else:
        chunks = _chunk_by_characters(text, chunk_size, overlap)

    logging.info(f"Generated {len(chunks)} chunks")

    return chunks


# -----------------------------
# Line-based chunking (logs)
# -----------------------------
def _chunk_by_lines(text: str, lines_per_chunk: int = 20) -> List[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    chunks = []
    for i in range(0, len(lines), lines_per_chunk):
        chunk = "\n".join(lines[i:i + lines_per_chunk])
        chunks.append(chunk)

    return chunks


# -----------------------------
# Paragraph-based chunking
# -----------------------------
def _chunk_by_paragraphs(text: str, chunk_size: int, overlap: int) -> List[str]:
    paragraphs = re.split(r'\n\s*\n', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) <= chunk_size:
            current += ("\n\n" + para) if current else para
        else:
            if current:
                chunks.append(current)

            # If paragraph too large → split further
            if len(para) > chunk_size:
                sub_chunks = _chunk_by_characters(para, chunk_size, overlap)
                chunks.extend(sub_chunks[:-1])
                current = sub_chunks[-1]
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


# -----------------------------
# Character-based fallback
# -----------------------------
def _chunk_by_characters(text: str, chunk_size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks