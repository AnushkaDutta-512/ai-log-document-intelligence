import os
from pypdf import PdfReader
from fastapi import HTTPException

def extract_text_from_file(file_path: str) -> str:
    """Extracts text from PDF, TXT, or LOG files."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext in {".txt", ".log"}:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for extraction")
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error extracting text: str({e})")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Extracted text is empty")
        
    return text.strip()
