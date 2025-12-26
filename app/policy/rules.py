INJECTION_PATTERNS = [
    # Most common direct injections
    "ignore all previous instructions",
    "ignore previous instructions",
    "ignore all instructions",
    "disregard above",
    "disregard previous instructions",
    "forget previous instructions",

    # Attempts to reveal hidden content / system prompt
    "reveal system prompt",
    "show system prompt",
    "print system prompt",
    "leak system prompt",
    "developer message",
    "system message",

    # Attempts to exfiltrate context / prompt / data
    "output the raw context",
    "output raw context",
    "print the context",
    "print context",
    "show the context",
    "dump the context",
    "return the context",
    "repeat the context",
    "as-is",

    # Role override patterns
    "act as",
    "you are now",
    "from now on",
]


def detect_prompt_injection(query: str) -> list[str]:
    """
    Detect common prompt injection attempts.
    Returns list of matched patterns (empty list if none).
    """
    q = (query or "").lower()
    return [p for p in INJECTION_PATTERNS if p in q]
