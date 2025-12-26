from dataclasses import dataclass
from typing import List
from app.ingest.loaders import Page


@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    page_num: int
    text: str


def chunk_pages(
    pages: List[Page],
    chunk_size: int = 2200,
    overlap: int = 250
) -> List[Chunk]:
    chunks: List[Chunk] = []

    for p in pages:
        text = p.text
        start = 0
        idx = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = f"{p.doc_id}-p{p.page_num}-c{idx}"
                chunks.append(Chunk(
                    doc_id=p.doc_id,
                    chunk_id=chunk_id,
                    page_num=p.page_num,
                    text=chunk_text
                ))

            idx += 1
            if end == len(text):
                break
            start = max(0, end - overlap)

    return chunks
