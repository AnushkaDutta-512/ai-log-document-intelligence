# AI Log & Document Intelligence (RAG System)

This document explains the architecture, concepts, and working of the system.
________________________________________
1. What the Project Does
Upload any document (PDF, TXT, LOG) and ask natural language questions about it. The system finds the most relevant parts of the document and uses Google Gemini to generate a proper conversational answer.
Tech used: FastAPI + SentenceTransformers + FAISS + Google Gemini + Docker
________________________________________
2. The RAG Pipeline 
RAG = Retrieval-Augmented Generation
Instead of asking an LLM to answer from memory, we:
1.	Store document content in a vector database
2.	When a question is asked, retrieve the most relevant chunks
3.	Pass those chunks + the question to an LLM to generate an answer
Why RAG?
•	LLMs hallucinate (make things up) when they don't know something
•	RAG grounds the answer in real document content
•	Works for any custom document without retraining the model
Our pipeline step by step:
Upload → Extract Text → Chunk → Embed → Store in FAISS
                                              ↓
                    Query → Embed Query → Search FAISS → Top Chunks
                                                              ↓
                                          Send to Gemini → Answer
________________________________________
3. Key Concepts
Embeddings
•	Text converted into a list of numbers (a vector)
•	Similar meaning = vectors close together in space
•	We use SentenceTransformers (all-MiniLM-L6-v2) — a lightweight BERT-based model
•	Produces 384-dimensional vectors (each text = list of 384 numbers)
•	Runs locally, no API key needed
Example:
•	"What is the course name?" → [0.23, -0.45, 0.11, ... 384 numbers]
•	"Course title and code" → [0.21, -0.43, 0.13, ...] ← close to above
•	"I like pizza" → [-0.89, 0.34, -0.67, ...] ← far from above
Chunking
•	Documents are too long to embed as one piece
•	We split them into overlapping chunks (~500 characters, 100 char overlap)
•	Overlap ensures sentences at boundaries aren't lost
•	PDFs use paragraph-based chunking
•	Log files use line-based chunking (20 lines per chunk)
FAISS (Vector Database)
•	FAISS = Facebook AI Similarity Search
•	Stores all chunk embeddings as vectors
•	When you query, it finds the chunks with smallest distance to your query vector
•	Uses L2 (Euclidean) distance — smaller = more similar
•	Index saved as faiss.index, metadata saved as metadata.pkl
•	Used in production by Meta, Spotify, and many others
Google Gemini API
•	Google's LLM (Large Language Model)
•	We send it: retrieved chunks (context) + user's question
•	It generates a proper conversational answer
•	Accessed via google-generativeai Python library
•	API key stored in .env file as GEMINI_API_KEY
•	Free tier available at aistudio.google.com
________________________________________
4. Tech Stack Explained
Technology	What it is	Why we used it
FastAPI	Python web framework	Fast, modern, auto-generates API docs at /docs
SentenceTransformers	Local embedding model	Free, no API key, runs on CPU
FAISS	Vector database	Industry standard for similarity search
Google Gemini	LLM for answer generation	Free API, generates natural language answers
PyPDF	PDF text extraction	Reads text from PDF files
python-dotenv	Environment variables	Keeps API keys out of code
Docker	Containerization	Run anywhere with one command
________________________________________
5. API Endpoints
Endpoint	Method	What it does
/health	GET	Check if server is running
/upload	POST	Upload a PDF/TXT/LOG file
/query	POST/GET	Ask a question, get RAG answer
________________________________________
6. What is an LLM?
Large Language Model — a neural network trained on massive amounts of text that can understand and generate human language.
Examples: GPT-4 (OpenAI), Gemini (Google), Llama (Meta), Claude (Anthropic)
How they work (simplified):
•	Trained to predict the next word given previous words
•	Learn patterns, facts, and reasoning from training data
•	We use them via API — send a prompt, get a response
Our use: We use Gemini as the "answer generator" in our RAG pipeline. We don't fine-tune it — we just send it context + question.
________________________________________
7. What is a Vector Database?
A database optimised for storing and searching vectors (embeddings).
Regular database: search by exact match or keyword Vector database: search by semantic similarity
How FAISS works:
1.	Store: add vectors → FAISS builds an index
2.	Search: give query vector → FAISS returns k nearest vectors
3.	We retrieve the text chunks associated with those vectors
Other vector databases: Pinecone, Weaviate, Chroma, Milvus FAISS is open source and runs locally — good for projects.
________________________________________
8. Docker
Packages the entire application into a container — Python, all libraries, and code bundled together.
Without Docker: Install Python, install 10 packages, hope versions match, run server With Docker: docker run -p 8000:8000 image-name — that's it
Key terms:
•	Image — blueprint of the app (like a recipe)
•	Container — running instance of the image (like a cooked dish)
•	Dockerfile — instructions to build the image
•	docker build — creates the image
•	docker run — starts a container from the image
________________________________________
9. Key Points
•	RAG is Retrieval-Augmented Generation. We use it because LLMs don't know the content of our specific documents. RAG retrieves relevant chunks from the document first, then passes them to the LLM so the answer is grounded in real content rather than hallucinated.
•	FAISS is a vector database by Facebook AI. It stores document chunks as 384-dimensional vectors. When a query comes in, we convert it to a vector and FAISS finds the chunks with the smallest L2 distance — meaning most semantically similar.
•	Gemini is the LLM that generates the final answer. We send it the retrieved document chunks as context plus the user's question, and it produces a natural language response.
•	Chunking splits a large document into smaller pieces before embedding. We can't embed a whole 50-page PDF as one vector — it loses detail. Smaller chunks give more precise retrieval.
