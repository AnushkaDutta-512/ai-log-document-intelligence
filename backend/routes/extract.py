from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.text_extraction import extract_text_from_file

router = APIRouter(prefix="/extract", tags=["Extract"])


class ExtractRequest(BaseModel):
    file_path: str


class ExtractResponse(BaseModel):
    file_path: str
    text: str


@router.post("/", response_model=ExtractResponse)
async def extract_text(request: ExtractRequest):
    """Extracts text from a given file path."""

    if not request.file_path:
        raise HTTPException(status_code=400, detail="File path is required")

    text = extract_text_from_file(request.file_path)

    return ExtractResponse(
        file_path=request.file_path,
        text=text
    )