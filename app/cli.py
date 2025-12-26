import argparse
import json
import os

from app.ingest.loaders import load_pdf
from app.ingest.chunking import chunk_pages
from app.ingest.embed_store import build_and_persist
from app.rag.extract import analyze_document
from app.eval.run import run_all


def ingest_pdf(file_path: str, doc_id: str) -> int:
    pages = load_pdf(file_path, doc_id=doc_id)
    chunks = chunk_pages(pages)

    rows = [{
        "doc_id": c.doc_id,
        "chunk_id": c.chunk_id,
        "page_num": c.page_num,
        "text": c.text
    } for c in chunks]

    build_and_persist(rows)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description="LLM Document Analysis Assistant")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest a PDF and build FAISS index")
    p_ingest.add_argument("--file", required=True, help="Path to PDF")
    p_ingest.add_argument("--doc-id", default="doc", help="Document identifier")

    p_analyze = sub.add_parser("analyze", help="Analyze using RAG + JSON extraction")
    p_analyze.add_argument("--query", required=True)
    p_analyze.add_argument("--top-k", type=int, default=5)
    p_analyze.add_argument("--out", default=None, help="Path to save JSON output")

    p_eval = sub.add_parser("eval", help="Run basic eval suite")
    p_eval.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()

    if args.cmd == "ingest":
        if not os.path.exists(args.file):
            raise SystemExit(f"File not found: {args.file}")

        n = ingest_pdf(args.file, args.doc_id)

        print(f"doc_id={args.doc_id} chunks={n}")
        print("Saved: data/chunks.jsonl")
        print("Saved: data/faiss.index")

    elif args.cmd == "analyze":
        result = analyze_document(args.query, top_k=args.top_k)
        payload = result.model_dump()

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"Saved: {args.out}")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.cmd == "eval":
        raise SystemExit(run_all(top_k=args.top_k))


if __name__ == "__main__":
    main()
