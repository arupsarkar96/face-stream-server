import json
import math
import os
import time
from typing import List, Dict

import faiss
import numpy as np

from app.schemas.result import ResultItem, FaissSearchResult  # <-- defined Pydantic models


class FaissIndexManager:
    def __init__(self,
                 dim: int = 512,
                 index_path: str = "face_index.faiss",
                 metadata_path: str = "face_metadata.json"):
        self.dim = dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata: List[Dict] = []

        if self.files_exist():
            self.load()
            print(f"[FAISS] Loaded index with {self.index.ntotal} vectors.")
        else:
            print("[FAISS] No index found. Awaiting external build.")

    def files_exist(self) -> bool:
        return os.path.exists(self.index_path) and os.path.exists(self.metadata_path)

    def build(self, embeddings: List[List[float]], metadata: List[Dict]):
        """Build the FAISS index from provided embeddings and metadata."""
        if not embeddings or not metadata:
            raise ValueError("Embeddings and metadata must be non-empty.")

        arr = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(arr)

        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(arr)
        self.metadata = metadata
        self.save()
        print(f"[FAISS] Built index with {len(embeddings)} entries.")

    def save(self):
        if self.index is None:
            raise RuntimeError("No index to save.")
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.metadata_path, "r") as f:
            self.metadata = json.load(f)

    def reset(self):
        self.index = faiss.IndexFlatIP(self.dim)
        self.metadata = []
        self.save()
        print("[FAISS] Index reset complete.")

    def add_embedding(self, embedding: List[float], person_id: str):
        """Add a new embedding to the index."""
        if self.index is None:
            raise RuntimeError("Index is not initialized. Call build() first.")
        emb = np.array([embedding], dtype="float32")
        faiss.normalize_L2(emb)
        self.index.add(emb)
        self.metadata.append({"person_id": person_id})
        self.save()
        print(f"[FAISS] Added embedding for person_id={person_id} New size {self.index.ntotal}")

    def search(self,
               query_embedding: List[float],
               top_k: int = 5,
               threshold: float = 0.6) -> FaissSearchResult:
        """Search the index for similar embeddings."""
        if self.index is None or self.index.ntotal == 0:
            return FaissSearchResult(
                matches=[],
                search_time_ms=0,
                entries_searched=0
            )

        start_time = time.time()

        query = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(query)
        scores, indices = self.index.search(query, top_k)

        matches: List[ResultItem] = []
        for idx, score in zip(indices[0], scores[0]):
            if not math.isfinite(score) or score < 0:
                continue
            similarity = float(f"{min(max(score, 0.0), 1.0):.2f}")
            if idx < len(self.metadata) and similarity >= threshold:
                person_id = self.metadata[idx].get("person_id")
                matches.append(ResultItem(person_id=person_id, similarity=similarity))

        elapsed_ms = int((time.time() - start_time) * 1000)

        return FaissSearchResult(
            matches=matches,
            search_time_ms=elapsed_ms,
            entries_searched=self.index.ntotal
        )
