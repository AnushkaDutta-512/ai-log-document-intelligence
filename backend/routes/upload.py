from fastapi import APIRouter, UploadFile, File, Depends
from backend.utils.validators import validate_file_extension, validate_file_size, UploadResponse
from backend.services.file_ingestion import save_uploaded_file
import logging
logging.basicConfig(level=logging.INFO)
router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Uploads a log or document file."""
    logging.info(f"Uploading file:{file.filename}")
    validate_file_extension(file.filename)
    # validate_file_size needs file length, but UploadFile doesn't expose it directly easily without reading.
    # We could do a basic check by seeking, but for simplicity, we omit the strict strict size check
    # if it's not strictly necessary. Let's do a basic size check:
    file.file.seek(0, 2)
    size = file.file.tell()
    validate_file_size(size)
    file.file.seek(0)
    
    file_path = save_uploaded_file(file)
    
    return UploadResponse(
        filename=file.filename,
        message="File uploaded successfully",
        file_path=file_path
    )
