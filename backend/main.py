from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from backend.routes.health import router as health_router
from backend.routes.upload import router as upload_router
from backend.routes.extract import router as extract_router
from backend.routes.chunk import router as chunk_router
from backend.routes.embed import router as embed_router
from backend.routes.store import router as store_router
from backend.routes.search import router as search_router
from backend.routes.query import router as query_router

app = FastAPI(
    title="AI Log & Document Intelligence",
    version="0.1.0",
    description="A complete backend system for RAG-based document AI."
)

# Optional: Add CORS middleware if a frontend will consume this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(extract_router)
app.include_router(chunk_router)
app.include_router(embed_router)
app.include_router(store_router)
app.include_router(search_router)
app.include_router(query_router)

# Mount static files
os.makedirs("backend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def serve_ui():
    """Serves the simple frontend UI."""
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        return f.read()
