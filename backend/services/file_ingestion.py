import os
import shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file safely"""

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Fix overwrite
    if os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, f"copy_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path