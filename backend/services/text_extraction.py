import os
import pdfplumber
from fastapi import HTTPException

def extract_text_from_file(file_path: str) -> str:
    """Extracts text from PDF, TXT, or LOG files."""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        elif ext in {".txt", ".log"}:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for extraction")
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Extracted text is empty")
        
    return text.strip()
