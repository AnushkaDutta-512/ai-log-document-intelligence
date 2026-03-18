from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Backend is running"}
