import faiss
import numpy as np
import os

import json
from typing import List, Dict, Any

METADATA_FILE = "faiss_metadata.json"
INDEX_FILE = "faiss_index.bin"
INDEX_DIR = "vector_store_data"

class FAISSStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[Dict[str, Any]] = []
        os.makedirs(INDEX_DIR, exist_ok=True)
        self.index_path = os.path.join(INDEX_DIR, INDEX_FILE)
        self.metadata_path = os.path.join(INDEX_DIR, METADATA_FILE)

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]]):
        """Adds embeddings and corresponding metadata."""
        if len(embeddings) != len(metadatas):
            raise ValueError("Number of embeddings and metadatas must match.")
            
        if len(embeddings) == 0:
            return
            
        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        return len(embeddings)

    def save(self):
        """Saves the FAISS index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        """Loads the FAISS index and metadata from disk if they exist."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)

    def get_all_filenames(self) -> List[str]:
        """Returns a list of all unique filenames currently in the index."""
        filenames = set()
        for meta in self.metadata:
            if "filename" in meta:
                filenames.add(meta["filename"])
        return sorted(list(filenames))

    def delete_by_filename(self, filename: str) -> int:
        """Deletes all chunks associated with a specific filename.
        Rebuilds the IndexFlatL2 since it doesn't natively support dynamic deletion."""
        indices_to_keep = [i for i, meta in enumerate(self.metadata) if meta.get("filename") != filename]
        deleted_count = len(self.metadata) - len(indices_to_keep)
        
        if deleted_count == 0:
            return 0
            
        new_index = faiss.IndexFlatL2(self.dimension)
        new_metadata = []
        
        if indices_to_keep:
            embeddings_to_keep = np.array([self.index.reconstruct(i) for i in indices_to_keep])
            new_index.add(embeddings_to_keep)
            new_metadata = [self.metadata[i] for i in indices_to_keep]
            
        self.index = new_index
        self.metadata = new_metadata
        self.save()
        return deleted_count

    def search(self, query_embedding: np.ndarray, k: int = 5, source_filter: str = None) -> List[Dict[str, Any]]:
        """
        Searches the index for the top k closest vectors.
        Includes a naive source_filter by over-fetching and filtering manually.
        """
        if self.index.ntotal == 0:
            return []
            
        # If filtering, fetch more to ensure we get k after filtering
        fetch_k = min(self.index.ntotal, k * 5) if source_filter else min(self.index.ntotal, k)
        
        distances, indices = self.index.search(query_embedding, fetch_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # faiss returns -1 if there aren't enough results
                continue
                
            meta = self.metadata[idx]
            
            # Use source_filter to filter by exact filename now
            if source_filter and meta.get("filename") != source_filter:
                continue
                
            results.append({
                "chunk_id": int(idx),
                "score": float(distances[0][i]),
                "text": meta.get("text"),
                "source": meta.get("source")
            })
            
            if len(results) >= k:
                break
                
        return results

# Singleton instance for the app
store = FAISSStore(dimension=384)
try:
    store.load()
except Exception as e:
    print(f"Failed to load FAISS store: {e}")
=======
import pickle

INDEX_FILE = "faiss.index"
METADATA_FILE = "metadata.pkl"


class FAISSStore:
    def __init__(self, dimension: int):
        self.dimension = dimension

        if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(METADATA_FILE, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []

    def add_embeddings(self, embeddings, metadatas):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadata.extend(metadatas)

    def save(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(METADATA_FILE, "wb") as f:
            pickle.dump(self.metadata, f)

    def search(self, query_embedding, k=5, source_filter: str = None):
        if self.index.ntotal == 0:
            return []

        # Search more candidates if filtering by source, to ensure enough results
        search_k = k * 5 if source_filter else k
        query_vector = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_vector, search_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            if idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]

            # Filter by source filename if provided
            if source_filter and source_filter not in meta.get("source", ""):
                continue

            results.append({
                "text": meta["text"],
                "source": meta.get("source", "unknown"),
                "chunk_id": meta.get("chunk_id", idx),
                "score": float(distances[0][i])
            })

            if len(results) >= k:
                break

        return results