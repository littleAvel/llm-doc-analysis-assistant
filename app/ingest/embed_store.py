import os
import json
from typing import List, Dict, Any

import numpy as np
import faiss
from openai import OpenAI

from app.config import OPENAI_API_KEY, EMBEDDING_MODEL, DATA_DIR


client = OpenAI(api_key=OPENAI_API_KEY)

CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")


def save_jsonl(path: str, rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def embed_texts(texts: List[str], batch_size: int = 64) -> np.ndarray:
    """
    Returns (N, D) float32 embeddings matrix.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env")

    vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        vectors.extend([d.embedding for d in resp.data])

    arr = np.array(vectors, dtype=np.float32)
    return arr


def build_faiss_index(vectors: np.ndarray) -> faiss.Index:
    """
    Uses inner product with L2-normalized vectors (cosine similarity).
    """
    if vectors.ndim != 2:
        raise ValueError("vectors must be a 2D array")

    faiss.normalize_L2(vectors)
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    return index


def persist_index(index: faiss.Index, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    faiss.write_index(index, path)


def build_and_persist(chunks_rows: List[Dict[str, Any]]) -> None:
    """
    Saves chunks.jsonl and faiss.index to disk.
    """
    save_jsonl(CHUNKS_PATH, chunks_rows)
    vectors = embed_texts([r["text"] for r in chunks_rows])
    index = build_faiss_index(vectors)
    persist_index(index, INDEX_PATH)
