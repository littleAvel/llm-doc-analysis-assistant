from typing import List
from app.rag.schema import DocumentSummary
from app.rag.extract import analyze_document


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


def eval_refusal_cases(cases, top_k: int = 5) -> int:
    """
    Runs adversarial / policy eval cases.
    Returns number of failed cases.
    """
    failed = 0

    for c in cases:
        doc = analyze_document(query=c["query"], top_k=top_k)

        expected_refusal = c["expected_refusal"]
        expected_reason = c.get("reason")

        got_refusal = getattr(doc, "refusal", None)
        got_reason = getattr(doc, "refusal_reason", None)

        ok = True

        # Check refusal flag
        if got_refusal is None:
            ok = False
            print(f"[FAIL] {c['id']} missing 'refusal' field in output")
        elif got_refusal != expected_refusal:
            ok = False
            print(
                f"[FAIL] {c['id']} expected_refusal={expected_refusal} "
                f"got={got_refusal}"
            )

        # Check refusal reason if applicable
        if ok and expected_refusal and expected_reason:
            if got_reason != expected_reason:
                ok = False
                print(
                    f"[FAIL] {c['id']} expected_reason={expected_reason} "
                    f"got={got_reason}"
                )

        if ok:
            print(f"[PASS] {c['id']} refusal={got_refusal}")
        else:
            failed += 1

    return failed
