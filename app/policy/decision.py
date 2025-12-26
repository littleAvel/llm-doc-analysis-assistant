from enum import Enum
from dataclasses import dataclass


class Decision(Enum):
    ALLOW = "allow"
    REFUSE = "refuse"


@dataclass
class PolicyResult:
    decision: Decision
    reasons: list[str]
