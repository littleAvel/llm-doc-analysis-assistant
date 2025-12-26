from app.policy.decision import Decision, PolicyResult
from app.policy.rules import detect_prompt_injection


def detect_secret_exfiltration(query: str) -> bool:
    """
    Detect attempts to extract secrets (API keys, env vars, .env contents, etc.).
    This should map to Decision.REFUSE with reason 'unsafe_request'.
    """
    q = (query or "").lower()

    SECRET_KEYWORDS = [
        # API keys
        "api key",
        "apikey",
        "openai_api_key",
        "openai key",
        "sk-",
        # Environment / secrets access
        "environment variable",
        "env var",
        "dotenv",
        ".env",
        "os.environ",
        "process.env",
        "read environment",
        "from the environment variable",
        "print the api key",
        "show the api key",
        "dump env",
    ]

    return any(k in q for k in SECRET_KEYWORDS)


def evaluate_policy(query: str) -> PolicyResult:
    """
    Lightweight policy gate for the CLI.
    Priority:
      1) Prompt injection (more specific): refuse with 'prompt_injection'
      2) Secret exfiltration / unsafe requests: refuse with 'unsafe_request'
      3) Otherwise allow
    """
    # 1) Prompt injection should win (more specific)
    if detect_prompt_injection(query):
        return PolicyResult(Decision.REFUSE, ["prompt_injection"])

    # 2) Secret exfiltration / unsafe requests
    if detect_secret_exfiltration(query):
        return PolicyResult(Decision.REFUSE, ["unsafe_request"])

    return PolicyResult(Decision.ALLOW, [])
