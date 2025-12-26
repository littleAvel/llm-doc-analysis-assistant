from dataclasses import dataclass
import fitz  # PyMuPDF


@dataclass
class Page:
    doc_id: str
    page_num: int
    text: str


def load_pdf(path: str, doc_id: str) -> list[Page]:
    """
    Load a PDF file and return a list of pages with cleaned text.
    """
    doc = fitz.open(path)
    pages: list[Page] = []

    for i in range(len(doc)):
        raw_text = doc[i].get_text("text") or ""
        cleaned_text = " ".join(raw_text.split())

        if cleaned_text.strip():
            pages.append(
                Page(
                    doc_id=doc_id,
                    page_num=i + 1,
                    text=cleaned_text
                )
            )

    return pages
