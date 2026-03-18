import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    # health.py endpoint
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_upload_and_extract():
    # Create a dummy txt file
    with open("dummy.txt", "w") as f:
        f.write("This is a test document.")
        
    try:
        # Test Upload
        with open("dummy.txt", "rb") as f:
            response = client.post("/upload", files={"file": ("dummy.txt", f, "text/plain")})
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "dummy.txt"
        file_path = data["file_path"]
        
        # Test Extract
        ext_response = client.post("/extract", json={"file_path": file_path})
        assert ext_response.status_code == 200
        assert "test document" in ext_response.json()["text"]
    finally:
        if os.path.exists("dummy.txt"):
            os.remove("dummy.txt")

def test_chunk():
    response = client.post("/chunk", json={
        "text": "Paragraph 1\n\nParagraph 2",
        "filename": "doc.txt"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["chunk_count"] == 2

def test_embed():
    # Using tiny strings so embedding is fast during tests
    response = client.post("/embed", json={"chunks": ["short text", "another one"]})
    assert response.status_code == 200
    data = response.json()
    assert data["chunk_count"] == 2
    assert data["embedding_dimension"] > 0
