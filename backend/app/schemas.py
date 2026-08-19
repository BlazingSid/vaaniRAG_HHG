from typing import Literal

from pydantic import BaseModel, Field


LanguageCode = Literal[
    "en-IN", "as-IN", "mr-IN", "hi-IN", "bn-IN", "gu-IN", "kn-IN", "ml-IN",
    "or-IN", "pa-IN", "ta-IN", "te-IN", "ur-IN", "ne-IN", "sa-IN",
]


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=400)
    language: LanguageCode = "en-IN"
    mode: Literal["fast", "generative"] = "fast"
    top_k: int = Field(default=5, ge=1, le=10)


class Evidence(BaseModel):
    id: str
    text: str
    score: float
    strategy: str
    query_id: str | None = None
    source: str = "ai4bharat/MSMARCO-XI"


class LatencyBreakdown(BaseModel):
    stt: float = 0.0
    guardrail: float = 0.0
    retrieval: float = 0.0
    generation: float = 0.0
    verification: float = 0.0
    total: float = 0.0


class QueryResponse(BaseModel):
    trace_id: str
    transcript: str | None = None
    answer: str
    grounded: bool
    abstained: bool
    confidence: float = Field(ge=0.0, le=1.0)
    mode: str
    evidence: list[Evidence]
    latency_ms: LatencyBreakdown
    guardrail_reason: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    collection: str
    vector_store_ready: bool
    sarvam_ready: bool
