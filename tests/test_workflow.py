import requests
import sys
import json

BASE_URL = "http://127.0.0.1:8000"

def log_step(name, data):
    print(f"\n--- {name} ---\n{json.dumps(data, indent=2)}")

def run_tests():
    # 1. Health
    res = requests.get(f"{BASE_URL}/health")
    log_step("Health Check", res.json())
    
    # 2. Upload
    filename = "test_doc.txt"
    with open(filename, "rb") as f:
        res = requests.post(f"{BASE_URL}/upload", files={"file": f})
    upload_data = res.json()
    log_step("Upload", upload_data)
    
    file_path = upload_data.get("file_path")
    
    # 3. Extract
    res = requests.post(f"{BASE_URL}/extract", json={"file_path": file_path})
    extract_data = res.json()
    log_step("Extract", extract_data)
    
    text = extract_data.get("text")
    
    # 4. Chunk
    res = requests.post(f"{BASE_URL}/chunk", json={"text": text, "filename": filename})
    chunk_data = res.json()
    log_step("Chunk", chunk_data)
    
    chunks = chunk_data.get("chunks")
    
    # 5. Embed
    res = requests.post(f"{BASE_URL}/embed", json={"chunks": chunks})
    embed_data = res.json()
    log_step("Embed", embed_data)
    
    # 6. Store
    res = requests.post(f"{BASE_URL}/store", json={"filename": filename, "chunks": chunks, "source": "txt"})
    store_data = res.json()
    log_step("Store", store_data)
    
    # 7. Search
    query = "What is FAISS?"
    res = requests.post(f"{BASE_URL}/search", json={"query": query, "k": 2})
    search_data = res.json()
    log_step("Search", search_data)
    
    # 8. Query (RAG)
    res = requests.post(f"{BASE_URL}/query", json={"query": query, "k": 2})
    query_data = res.json()
    log_step("Query", query_data)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)
