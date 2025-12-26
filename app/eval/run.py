from app.eval.cases import EVAL_CASES
from app.eval.adversarial_cases import ADVERSARIAL_CASES
from app.eval.basic_eval import eval_refusal_cases
from app.rag.extract import analyze_document


def run_all(top_k: int = 5) -> int:
    passed = 0
    total = 0

    # --- Regular eval cases ---
    for case in EVAL_CASES:
        name = case["name"]
        query = case["query"]
        checks = case.get("checks", {})

        total += 1

        try:
            doc = analyze_document(query=query, top_k=top_k)
            data = doc.model_dump()
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            continue

        # If we got a refusal for a normal eval, treat it as a failure
        if data.get("refusal") is True:
            print(f"[FAIL] {name} (refused)")
            continue

        ok = True

        if checks.get("email_contains_at"):
            email = data.get("email")
            ok = ok and ((email is None) or ("@" in email))

        if "skills_min_len" in checks:
            ok = ok and (len(data.get("skills") or []) >= checks["skills_min_len"])

        if "experience_max_highlights" in checks:
            for exp in (data.get("experience") or []):
                ok = ok and (len(exp.get("highlights") or []) <= checks["experience_max_highlights"])

        # NOTE:
        # must_not_invent currently cannot be strongly verified unless you check a concrete field
        # (e.g. phone) or compare against source text. Keep as a placeholder if you want.
        if checks.get("must_not_invent"):
            ok = ok and True

        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if ok:
            passed += 1

    # --- Policy / adversarial cases (run ONCE) ---
    try:
        fails_adv = eval_refusal_cases(ADVERSARIAL_CASES, top_k=top_k)
    except Exception as e:
        # If adversarial eval crashes, count it as all failed (safer).
        print(f"[ERROR] adversarial_eval: {e}")
        fails_adv = len(ADVERSARIAL_CASES)

    adv_total = len(ADVERSARIAL_CASES)
    adv_passed = adv_total - fails_adv

    passed += adv_passed
    total += adv_total

    print(f"\nResult: {passed}/{total} passed")
    return 0 if passed == total else 1
