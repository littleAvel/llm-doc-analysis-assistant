from typing import List
from app.rag.schema import DocumentSummary


def run_basic_eval(result: DocumentSummary) -> List[str]:
    """
    Basic quality checks for LLM extraction results.
    Returns a list of error messages. Empty list = passed.
    """
    errors: List[str] = []

    # High-level sanity checks
    if not result.summary_points:
        errors.append("summary_points is empty")

    if not result.skills:
        errors.append("skills is empty")

    # Experience-level checks
    for i, exp in enumerate(result.experience):
        if not exp.company:
            errors.append(f"experience[{i}].company missing")

        if exp.highlights and len(exp.highlights) > 5:
            errors.append(f"experience[{i}].highlights too long")

        for h in exp.highlights:
            if len(h) > 300:
                errors.append(f"experience[{i}].highlight too verbose")

    return errors
