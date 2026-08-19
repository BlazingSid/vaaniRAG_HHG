import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardDecision:
    allowed: bool
    reason: str | None = None
    category: str | None = None


INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.I),
    re.compile(r"reveal\s+(the\s+)?(system|developer)\s+prompt", re.I),
    re.compile(r"act\s+as\s+(an?\s+)?unrestricted", re.I),
    re.compile(r"सूचना\s+दुर्लक्ष", re.I),
)

UNSAFE_PATTERNS = (
    re.compile(r"(?:build|make|assemble).{0,24}(?:bomb|explosive)", re.I),
    re.compile(r"(?:steal|phish|harvest).{0,24}(?:password|credit card|otp)", re.I),
    re.compile(r"(?:write|create).{0,24}(?:ransomware|credential stealer)", re.I),
    re.compile(r"(?:hurt|kill).{0,16}(?:myself|someone|person)", re.I),
)


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).lower()
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def screen_input(question: str) -> GuardDecision:
    value = question.strip()
    if len(value) < 3:
        return GuardDecision(False, "The question is too short.", "invalid")
    if len(value) > 400:
        return GuardDecision(False, "The question exceeds 400 characters.", "invalid")
    if any(pattern.search(value) for pattern in INJECTION_PATTERNS):
        return GuardDecision(False, "Prompt-injection pattern detected.", "injection")
    if any(pattern.search(value) for pattern in UNSAFE_PATTERNS):
        return GuardDecision(False, "Unsafe instructional request detected.", "unsafe")
    return GuardDecision(True)


def content_tokens(text: str) -> set[str]:
    return {token for token in normalize(text).split() if len(token) > 2}


def lexical_coverage(question: str, evidence: str) -> float:
    query_tokens = content_tokens(question)
    if not query_tokens:
        return 0.0
    return len(query_tokens & content_tokens(evidence)) / len(query_tokens)


def answer_support(answer: str, evidence: str) -> float:
    answer_tokens = content_tokens(answer)
    if not answer_tokens:
        return 0.0
    return len(answer_tokens & content_tokens(evidence)) / len(answer_tokens)


def retrieval_confidence(question: str, evidence: str, rrf_score: float) -> float:
    # RRF expresses rank agreement, not semantic calibration. Lexical coverage is
    # therefore kept as an independent grounding signal rather than treating the
    # fused score as a cosine similarity.
    lexical = lexical_coverage(question, evidence)
    rank_agreement = max(0.0, min(1.0, rrf_score))
    return max(0.0, min(1.0, 0.58 * lexical + 0.42 * rank_agreement))
