from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )

    embeddings = [item.embedding for item in response.data]
    return embeddings
