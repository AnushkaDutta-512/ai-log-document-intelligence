# AI Log & Document Intelligence (RAG-based System)

## Project Overview
A complete, production-ready FastAPI backend for intelligent log and document analysis using a Retrieval-Augmented Generation (RAG) approach.

## Features
- Upload PDFs, TXTs, and LOGs
- Extract and chunk text intelligently based on file type
- Generate embeddings securely using local `SentenceTransformers`
- Store vectors in an efficient `FAISS` index
- Perform semantic searches and simulate an LLM-based RAG query response

## Tech Stack
- **Python 3.11**
- **FastAPI** & **Uvicorn**
- **SentenceTransformers** (`all-MiniLM-L6-v2`)
- **FAISS** (Facebook AI Similarity Search)
- **PyPDF**

## Architecture Pipeline
`upload → extract → chunk → embed → store → search → query`

## API Endpoints List
- `POST /upload`: Upload a log/document file.
- `POST /extract`: Extract raw text from the file path.
- `POST /chunk`: Break text into manageable pieces for vector search.
- `POST /embed`: Generate model embeddings from chunks.
- `POST /store`: Save the embeddings and metadata to FAISS.
- `POST /search`: Semantically search the index using a query.
- `POST /query`: Simulate a RAG response built from the retrieved contexts.

## How to Run Locally

### 1. Using Python Virtual Environment
```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Access the Swagger UI at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Using Docker
```bash
docker build -t ai-document-intelligence .
docker run -p 8000:8000 ai-document-intelligence
```

## Example Usage Flow
1. **Upload** a document using `/upload`.
2. Grab the file path and send it to `/extract`.
3. Send the extracted text to `/chunk`.
4. Submit the chunks to `/store` to build your vector database.
5. Use `/query` to ask questions about your uploaded documents!
