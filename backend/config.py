import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760")) # 10MB default
    PORT = int(os.getenv("PORT", "8000"))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

config = Config()
