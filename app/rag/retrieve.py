import os
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from openai import OpenAI

from app.config import OPENAI_API_KEY, EMBEDDING_MODEL, DATA_DIR
from app.ingest.embed_store import load_jsonl

client = OpenAI(api_key=OPENAI_API_KEY)

CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.jsonl")
INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")


def embed_query(query: str) -> np.ndarray:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env")

    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    vec = np.array(resp.data[0].embedding, dtype=np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    return vec


def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    if not os.path.exists(CHUNKS_PATH) or not os.path.exists(INDEX_PATH):
        raise RuntimeError("Index not found. Run ingestion first to create chunks.jsonl and faiss.index")

    rows = load_jsonl(CHUNKS_PATH)
    index = faiss.read_index(INDEX_PATH)

    qvec = embed_query(query)
    scores, ids = index.search(qvec, top_k)

    results: List[Dict[str, Any]] = []
    for score, idx in zip(scores[0].tolist(), ids[0].tolist()):
        if idx == -1:
            continue
        r = rows[idx]
        results.append({
            "score": float(score),
            "doc_id": r["doc_id"],
            "chunk_id": r["chunk_id"],
            "page_num": r["page_num"],
            "text": r["text"],
        })

    return results
