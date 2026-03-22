import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


# -----------------------------
# Health Check Test
# -----------------------------
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# -----------------------------
# Upload + Extract Test
# -----------------------------
def test_upload_and_extract():
    # Create a dummy file
    with open("dummy.txt", "w") as f:
        f.write("This is a test document.")

    try:
        # Upload
        with open("dummy.txt", "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("dummy.txt", f, "text/plain")}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "dummy.txt"

        file_path = data["file_path"]

        # Extract
        ext_response = client.post("/extract", json={"file_path": file_path})
        assert ext_response.status_code == 200

        extracted_text = ext_response.json()["text"]
        assert "test document" in extracted_text

    finally:
        if os.path.exists("dummy.txt"):
            os.remove("dummy.txt")


# -----------------------------
# Chunk Test
# -----------------------------
def test_chunk():
    response = client.post("/chunk", json={
        "text": "Paragraph 1\n\nParagraph 2",
        "filename": "doc.txt"
    })

    assert response.status_code == 200
    data = response.json()

    assert data["chunk_count"] > 0
    assert "chunks" in data


# -----------------------------
# Embed Test
# -----------------------------
def test_embed():
    response = client.post("/embed", json={
        "chunks": ["short text", "another one"]
    })

    assert response.status_code == 200
    data = response.json()

    assert data["chunk_count"] == 2
    assert data["embedding_dimension"] > 0


# -----------------------------
# RAG Query Test (IMPORTANT)
# -----------------------------
def test_query():
    response = client.post("/query", json={
        "query": "What is this document about?",
        "k": 2
    })

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert "sources" in data