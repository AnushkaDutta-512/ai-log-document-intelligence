import faiss
import numpy as np
import os
import pickle

INDEX_FILE = "faiss.index"
METADATA_FILE = "metadata.pkl"


class FAISSStore:
    def __init__(self, dimension: int):
        self.dimension = dimension

        if os.path.exists(INDEX_FILE):
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

    def search(self, query_embedding, k=5):
        query_vector = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(query_vector, k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results