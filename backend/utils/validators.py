import os
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.config import config

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".log"}
MAX_FILE_SIZE = config.MAX_FILE_SIZE

def validate_file_extension(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext

def validate_file_size(file_size: int):
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds maximum allowed size (10 MB)"
        )

class UploadResponse(BaseModel):
    filename: str
    message: str
    file_path: str
