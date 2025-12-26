EVAL_CASES = [
    {
        "name": "name_email_present_if_available",
        "query": "Extract person name and email if present in the document.",
        "checks": {"email_contains_at": True},
    },
    {
        "name": "skills_non_empty",
        "query": "Extract key skills mentioned in the document.",
        "checks": {"skills_min_len": 3},
    },
    {
        "name": "experience_non_empty_if_present",
        "query": "Extract experience items with company and highlights.",
        "checks": {"experience_max_highlights": 5},
    },
    {
        "name": "no_invention",
        "query": "Extract phone number.",
        "checks": {"must_not_invent": True},
    },
]
