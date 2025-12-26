import os
import faiss
from app.ingest.loaders import load_pdf
from app.ingest.chunking import chunk_pages
from app.ingest.embed_store import build_and_persist, CHUNKS_PATH, INDEX_PATH

pages = load_pdf("docs/sample.pdf", doc_id="sample")
chunks = chunk_pages(pages)

rows = [{
    "doc_id": c.doc_id,
    "chunk_id": c.chunk_id,
    "page_num": c.page_num,
    "text": c.text
} for c in chunks]

build_and_persist(rows)

print("Saved:", CHUNKS_PATH, "exists=", os.path.exists(CHUNKS_PATH))
print("Saved:", INDEX_PATH, "exists=", os.path.exists(INDEX_PATH))

index = faiss.read_index(INDEX_PATH)
print("Index size:", index.ntotal)
