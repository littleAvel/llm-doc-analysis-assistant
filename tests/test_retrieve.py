from app.rag.retrieve import search

query = "What are the candidate's key skills and focus areas?"
results = search(query, top_k=3)

for i, r in enumerate(results, 1):
    print(f"\n#{i} score={r['score']:.4f} chunk={r['chunk_id']} page={r['page_num']}")
    print(r["text"][:300])
