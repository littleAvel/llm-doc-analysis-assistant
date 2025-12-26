from app.ingest.loaders import load_pdf

pages = load_pdf("docs/sample.pdf", doc_id="sample")

print(f"Pages loaded: {len(pages)}")
print(pages[0].text[:500])
