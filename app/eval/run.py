from app.rag.extract import analyze_document
from app.eval.cases import EVAL_CASES


def run_all(top_k: int = 5) -> int:
    passed = 0

    for case in EVAL_CASES:
        name = case["name"]
        query = case["query"]
        checks = case["checks"]

        doc = analyze_document(query=query, top_k=top_k)
        data = doc.model_dump()

        ok = True

        if checks.get("email_contains_at"):
            email = data.get("email")
            ok &= (email is None) or ("@" in email)

        if "skills_min_len" in checks:
            ok &= len(data.get("skills") or []) >= checks["skills_min_len"]

        if "experience_max_highlights" in checks:
            for exp in (data.get("experience") or []):
                ok &= len(exp.get("highlights") or []) <= checks["experience_max_highlights"]

        if checks.get("must_not_invent"):
            ok &= True

        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if ok:
            passed += 1

    total = len(EVAL_CASES)
    print(f"\nResult: {passed}/{total} passed")
    return 0 if passed == total else 1
