# LLM Document Analysis Assistant

A production-oriented document analysis assistant built with a RAG pipeline (chunking → embeddings → FAISS retrieval) and guarded prompt engineering for deterministic, schema-validated JSON outputs.

This project focuses on reliability: structured extraction, validation, fail-safes, and lightweight evals.

---

## Features

- PDF ingestion (page-level loading)
- Text chunking with stable chunk IDs
- Embeddings + FAISS vector index
- Retrieval-Augmented Generation (RAG) for context building
- Guarded extraction prompts (anti-hallucination, deterministic outputs)
- Structured JSON output enforced by a Pydantic schema
- Fallback JSON repair strategy + validation
- Basic eval suite to test stability and quality
- CLI interface (`ingest`, `analyze`, `eval`)

---

## Quickstart

### 1) Setup

Create `.env` with your OpenAI key:

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
LOG_LEVEL=INFO
```

Install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Ingest a PDF and build the index
```
PYTHONPATH=. python -m app.cli ingest --file docs/sample.pdf --doc-id sample
```

Artifacts are stored in:

- `data/chunks.jsonl`

- `data/faiss.index`


### 3) Analyze with RAG + structured extraction

Print JSON to stdout:
```
PYTHONPATH=. python -m app.cli analyze --query "Extract key facts from the document."
```
Save JSON to a file:

```
PYTHONPATH=. python -m app.cli analyze \
  --query "Extract key facts from the document." \
  --out data/result.json
```

### 4) Run eval suite
```
PYTHONPATH=. python -m app.cli eval
```

Expected output ends with:
```
Result: 4/4 passed
```

## Architecture

1. **Ingestion:** PDF → text pages
2. **Chunking:** stable chunk IDs, chunk size/overlap strategy
3. **Indexing:** embeddings → FAISS index persistence
4. **Retrieval:** top-k chunks for a query
5. **Context building:** context length caps + structured formatting
6. **Extraction:** strict system prompt → JSON-only output
7. **Validation:** Pydantic schema + repair fallback
8. **Evals:** basic checks for stability and non-invention

## Reliability & Guardrails

- Temperature=0 (deterministic outputs)
- “Use only provided context” system shaping
- Context length limiting to prevent prompt overflow
- Schema enforcement via Pydantic
- Fallback JSON repair and re-validation
- Eval suite to catch regressions

## Notes

Current extraction schema is demonstrated on a sample resume-like PDF, but the pipeline is schema-driven and can be adapted to other business documents by changing the extraction schema and prompts.


## Future Improvements

- **Schema generalization:**  
  Support multiple document types (e.g. invoices, contracts, reports) by introducing pluggable extraction schemas and prompt templates.

- **Adaptive chunking strategies:**  
  Improve retrieval quality by experimenting with semantic chunking, section-aware chunking, or dynamic chunk sizes based on document structure.

- **Hybrid retrieval:**  
  Combine vector similarity search with keyword or metadata-based filtering (hybrid RAG) to improve precision on factual queries.

- **Confidence-aware extraction:**  
  Attach confidence scores or provenance (chunk references) to extracted fields to improve transparency and downstream trust.

- **Extended evaluation suite:**  
  Add regression tests for hallucination detection, schema drift, and retrieval quality using multiple documents and adversarial queries.

- **Service API layer:**  
  Expose the pipeline as a FastAPI service with request-level logging, rate limiting, and structured error handling for production use.

- **Cost and latency optimization:**  
  Introduce embedding caching, batching strategies, and model routing to reduce inference cost and improve throughput.
