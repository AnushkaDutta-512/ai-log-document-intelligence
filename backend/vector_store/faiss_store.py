import faiss
import numpy as np
import os
import json
from typing import List, Dict, Any

INDEX_DIR = "vector_store_data"
INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "faiss_metadata.json"


class FAISSStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata: List[Dict[str, Any]] = []

        os.makedirs(INDEX_DIR, exist_ok=True)

        self.index_path = os.path.join(INDEX_DIR, INDEX_FILE)
        self.metadata_path = os.path.join(INDEX_DIR, METADATA_FILE)

    # -----------------------------
    # Add embeddings
    # -----------------------------
    def add_embeddings(self, embeddings, metadatas):
        vectors = np.array(embeddings).astype("float32")

        if len(vectors) == 0:
            return 0

        self.index.add(vectors)
        self.metadata.extend(metadatas)
        return len(vectors)

    # -----------------------------
    # Save & Load
    # -----------------------------
    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

    # -----------------------------
    # Search
    # -----------------------------
    def search(self, query_embedding, k=5, source_filter=None):
        if self.index.ntotal == 0:
            return []

        query_vector = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_vector, k)

        results = []

        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            meta = self.metadata[idx]

            if source_filter and meta.get("filename") != source_filter:
                continue

            results.append({
                "text": meta.get("text"),
                "source": meta.get("source"),
                "filename": meta.get("filename"),
                "chunk_id": idx,
                "score": float(distances[0][i])
            })

        return results

    # -----------------------------
    # List files
    # -----------------------------
    def get_all_filenames(self):
        filenames = set()
        for meta in self.metadata:
            if "filename" in meta:
                filenames.add(meta["filename"])
        return list(filenames)

    # -----------------------------
    # Delete file
    # -----------------------------
    def delete_by_filename(self, filename: str) -> int:
        indices_to_keep = [
            i for i, meta in enumerate(self.metadata)
            if meta.get("filename") != filename
        ]

        deleted_count = len(self.metadata) - len(indices_to_keep)

        if deleted_count == 0:
            return 0

        new_index = faiss.IndexFlatL2(self.dimension)
        new_metadata = []

        if indices_to_keep:
            vectors = np.array(
                [self.index.reconstruct(i) for i in indices_to_keep]
            ).astype("float32")

            new_index.add(vectors)
            new_metadata = [self.metadata[i] for i in indices_to_keep]

        self.index = new_index
        self.metadata = new_metadata
        self.save()

        return deleted_count


# -----------------------------
# Singleton instance
# -----------------------------
store = FAISSStore(dimension=384)

try:
    store.load()
except Exception as e:
    print(f"FAISS load failed: {e}")