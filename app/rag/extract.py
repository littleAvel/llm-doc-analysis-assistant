import json
import logging
import time
from typing import Any, Dict, List

from openai import OpenAI
from pydantic import ValidationError

from app.config import OPENAI_API_KEY, LOG_LEVEL
from app.rag.schema import DocumentSummary
from app.rag.retrieve import search

client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger("llm_doc_assistant")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.setLevel(getattr(logging, str(LOG_LEVEL).upper(), logging.INFO))


MAX_CONTEXT_CHARS = 12_000
MODEL = "gpt-4.1-mini"

SYSTEM = """You are a strict information extraction engine.

Rules:
- Use ONLY the provided context.
- Do NOT infer or invent facts.
- If information is missing, return null or empty lists.
- Output ONLY valid JSON.
- No explanations, no commentary.
"""


def build_context(chunks: List[Dict[str, Any]]) -> str:
    parts: List[str] = []
    total = 0

    for c in chunks:
        block = f"[chunk_id={c['chunk_id']} page={c['page_num']}]\n{c['text']}"
        if total + len(block) > MAX_CONTEXT_CHARS:
            break
        parts.append(block)
        total += len(block)

    return "\n\n---\n\n".join(parts)


def extraction_prompt(context: str) -> str:
    return f"""
Extract structured information from the document context below.

Hard rules:
- Output must be VALID JSON matching the schema.
- Use ONLY facts explicitly present in the context.
- Do NOT add companies/roles/dates/skills that are not mentioned.
- If a field is unknown, use null or [].

Schema:
{{
  "candidate_name": string|null,
  "location": string|null,
  "email": string|null,
  "summary_points": [string],
  "skills": [string],
  "experience": [
    {{
      "company": string,
      "role": string|null,
      "start": string|null,
      "end": string|null,
      "highlights": [string]
    }}
  ]
}}

Output constraints:
- Keep lists concise (<= 8 skills, <= 3 highlights per experience unless clearly more).
- Remove duplicates and near-duplicates.

Context:
{context}
""".strip()


def call_llm(prompt: str) -> str:
    resp = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_output_tokens=800,
    )
    return resp.output_text


def extract_json_text(s: str) -> str:
    """
    Make model outputs JSON-parseable:
    - removes ```json fences if present
    - extracts the substring from first '{' to last '}'
    """
    if not s:
        return s

    s = s.strip()

    # Remove markdown fences if the model wrapped output as ```json ... ```
    if s.startswith("```"):
        # drop first line (``` or ```json)
        lines = s.splitlines()
        if lines:
            lines = lines[1:]
        # drop last line if it's ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        s = "\n".join(lines).strip()

    # Extract JSON object boundaries (robust against accidental prefix/suffix text)
    start_obj = s.find("{"); end_obj = s.rfind("}")
    start_arr = s.find("["); end_arr = s.rfind("]")

    if start_obj != -1 and end_obj != -1 and end_obj > start_obj:
        s = s[start_obj:end_obj+1].strip()
    elif start_arr != -1 and end_arr != -1 and end_arr > start_arr:
        s = s[start_arr:end_arr+1].strip()

    return s


def robust_parse(raw: str) -> DocumentSummary:
    # 1) try direct JSON parse
    try:
        raw_json = extract_json_text(raw)
        if not raw_json or ("{" not in raw_json and "[" not in raw_json):
            raise json.JSONDecodeError("Empty/non-JSON output", raw_json or "", 0)

        data = json.loads(raw_json)
        return DocumentSummary.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        pass

    # 2) fallback: repair JSON by asking the model to output valid JSON only
    repair = f"""
    Fix the following into VALID JSON only.
    Do not add keys not present in the schema.
    Return only JSON.

    RAW:
    {raw}
    """.strip()

    fixed = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": repair},
        ],
        temperature=0,
    ).output_text

    fixed_json = extract_json_text(fixed)

    if not fixed_json or ("{" not in fixed_json and "[" not in fixed_json):
        raise RuntimeError(f"Repair produced non-JSON output: {fixed[:200]!r}")

    data = json.loads(fixed_json)

    return DocumentSummary.model_validate(data)


def analyze_document(query: str, top_k: int = 5) -> DocumentSummary:
    t0 = time.perf_counter()

    logger.info(f"analyze_document: query_len={len(query)} top_k={top_k}")

    t_search = time.perf_counter()
    chunks = search(query, top_k=top_k)
    dt_search = (time.perf_counter() - t_search) * 1000

    context = build_context(chunks)
    context_chars = len(context)

    logger.info(
        f"retrieval: chunks_returned={len(chunks)} context_chars={context_chars} "
        f"search_ms={dt_search:.1f}"
    )

    if not context.strip():
        logger.warning("empty_context: returning empty schema (fail-safe)")
        return DocumentSummary()

    prompt = extraction_prompt(context)

    t_llm = time.perf_counter()
    raw = call_llm(prompt)
    dt_llm = (time.perf_counter() - t_llm) * 1000

    logger.info(
        f"llm: raw_chars={len(raw)} llm_ms={dt_llm:.1f}"
    )

    t_parse = time.perf_counter()
    result = robust_parse(raw)
    dt_parse = (time.perf_counter() - t_parse) * 1000

    total_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"done: parse_ms={dt_parse:.1f} total_ms={total_ms:.1f}")

    return result
