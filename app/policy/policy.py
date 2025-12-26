from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Decision(str, Enum):
    ALLOW = "allow"
    PARTIAL = "partial"
    REFUSE = "refuse"


@dataclass
class PolicyDecision:
    decision: Decision
    reasons: List[str]
    notes: Optional[str] = None


# Very simple heuristics. We keep it deterministic and explainable.
INJECTION_PATTERNS = [
    r"ignore (all|any|previous) instructions",
    r"system prompt",
    r"developer message",
    r"reveal.*(key|token|secret|password)",
    r"you are chatgpt",
    r"act as",
    r"jailbreak",
    r"bypass",
]


UNSAFE_REQUEST_PATTERNS = [
    r"api key",
    r"password",
    r"secret",
    r"private data",
]


def detect_prompt_injection(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in INJECTION_PATTERNS)


def detect_unsafe_request(query: str) -> bool:
    q = (query or "").lower()
    return any(re.search(p, q) for p in UNSAFE_REQUEST_PATTERNS)


def decide(query: str, context: str) -> PolicyDecision:
    reasons: List[str] = []

    # If user query asks for secrets/sensitive stuff — refuse.
    if detect_unsafe_request(query):
        reasons.append("unsafe_request")

    # If the provided context contains injection-like instructions — note it.
    if detect_prompt_injection(context):
        reasons.append("prompt_injection_in_context")

    # Decision logic
    if "unsafe_request" in reasons:
        return PolicyDecision(decision=Decision.REFUSE, reasons=reasons, notes="Request violates policy.")

    if "prompt_injection_in_context" in reasons:
        # Still allow extraction, but force strict ignoring of any instructions inside context.
        return PolicyDecision(decision=Decision.PARTIAL, reasons=reasons, notes="Context may contain injection. Extract facts only.")

    return PolicyDecision(decision=Decision.ALLOW, reasons=reasons)
