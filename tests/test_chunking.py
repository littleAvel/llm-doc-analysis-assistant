from app.ingest.loaders import load_pdf
from app.ingest.chunking import chunk_pages

pages = load_pdf("docs/sample.pdf", doc_id="sample")
chunks = chunk_pages(pages)

print("Pages:", len(pages))
print("Chunks:", len(chunks))
print("First chunk id:", chunks[0].chunk_id)
print("First chunk page:", chunks[0].page_num)
print("First chunk text preview:", chunks[0].text[:300])
