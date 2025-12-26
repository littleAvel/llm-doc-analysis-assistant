from app.rag.extract import analyze_document
from app.eval.basic_eval import run_basic_eval

result = analyze_document(
    "Extract candidate summary, skills, and experience.",
    top_k=5
)

errors = run_basic_eval(result)

print(result.model_dump_json(indent=2))

if errors:
    print("\nEVAL FAILED ❌")
    for e in errors:
        print("-", e)
else:
    print("\nEVAL PASSED ✅")
