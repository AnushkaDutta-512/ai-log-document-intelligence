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
