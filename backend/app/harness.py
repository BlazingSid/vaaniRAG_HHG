from __future__ import annotations

import asyncio
import time
import uuid

from .config import Settings
from .generation import GenerationError, SarvamGroundedGenerator
from .guardrails import answer_support, screen_input
from .retrieval import HybridRetriever, RetrievedHit
from .schemas import LatencyBreakdown, QueryRequest, QueryResponse


def _elapsed_ms(start: int) -> float:
    return (time.perf_counter_ns() - start) / 1_000_000


class QueryHarness:
    def __init__(
        self,
        settings: Settings,
        retriever: HybridRetriever,
        generator: SarvamGroundedGenerator,
    ):
        self.settings = settings
        self.retriever = retriever
        self.generator = generator

    async def run(
        self,
        request: QueryRequest,
        *,
        transcript: str | None = None,
        stt_ms: float = 0.0,
    ) -> QueryResponse:
        total_started = time.perf_counter_ns()
        guard_started = time.perf_counter_ns()
        decision = screen_input(request.question)
        guard_ms = _elapsed_ms(guard_started)

        if not decision.allowed:
            return self._abstain(
                request=request,
                trace_id=uuid.uuid4().hex,
                transcript=transcript,
                reason=decision.reason or "The request was blocked.",
                category=decision.category,
                stt_ms=stt_ms,
                guard_ms=guard_ms,
                total_ms=_elapsed_ms(total_started),
            )

        retrieval_started = time.perf_counter_ns()
        hits = await self._retrieve_with_retry(request)
        retrieval_ms = _elapsed_ms(retrieval_started)
        confidence = hits[0].confidence if hits else 0.0

        if not hits or confidence < self.settings.min_grounding_confidence:
            return self._abstain(
                request=request,
                trace_id=uuid.uuid4().hex,
                transcript=transcript,
                reason="The retrieved evidence was not strong enough to answer safely.",
                category="low_confidence",
                stt_ms=stt_ms,
                guard_ms=guard_ms,
                retrieval_ms=retrieval_ms,
                total_ms=_elapsed_ms(total_started),
                confidence=confidence,
                hits=hits,
            )

        mode = "fast"
        generation_ms = 0.0
        answer = hits[0].answer.strip()
        generative_requested = (
            request.mode == "generative"
            and self.settings.enable_generative_mode
            and self.generator.ready
            and _elapsed_ms(total_started) < self.settings.query_deadline_ms
        )
        if generative_requested:
            generation_started = time.perf_counter_ns()
            try:
                generated = await self.generator.generate(
                    request.question,
                    request.language,
                    hits,
                )
                if generated.supported:
                    answer = generated.text
                    mode = "generative"
            except GenerationError:
                mode = "fast_fallback"
            generation_ms = _elapsed_ms(generation_started)

        if not answer:
            return self._abstain(
                request=request,
                trace_id=uuid.uuid4().hex,
                transcript=transcript,
                reason="The source record did not contain an answer.",
                category="missing_answer",
                stt_ms=stt_ms,
                guard_ms=guard_ms,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                total_ms=_elapsed_ms(total_started),
                confidence=confidence,
                hits=hits,
            )

        verification_started = time.perf_counter_ns()
        evidence_text = " ".join(hit.parent_context for hit in hits)
        support = answer_support(answer, evidence_text)
        verification_ms = _elapsed_ms(verification_started)
        if support < 0.12:
            return self._abstain(
                request=request,
                trace_id=uuid.uuid4().hex,
                transcript=transcript,
                reason="The proposed answer was not sufficiently supported by the evidence.",
                category="ungrounded_answer",
                stt_ms=stt_ms,
                guard_ms=guard_ms,
                retrieval_ms=retrieval_ms,
                generation_ms=generation_ms,
                verification_ms=verification_ms,
                total_ms=_elapsed_ms(total_started),
                confidence=confidence,
                hits=hits,
            )

        return QueryResponse(
            trace_id=uuid.uuid4().hex,
            transcript=transcript,
            answer=answer,
            grounded=True,
            abstained=False,
            confidence=confidence,
            mode=mode,
            evidence=[hit.evidence for hit in hits],
            latency_ms=LatencyBreakdown(
                stt=stt_ms,
                guardrail=guard_ms,
                retrieval=retrieval_ms,
                generation=generation_ms,
                verification=verification_ms,
                total=_elapsed_ms(total_started) + stt_ms,
            ),
        )

    async def _retrieve_with_retry(self, request: QueryRequest) -> list[RetrievedHit]:
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                return await asyncio.to_thread(
                    self.retriever.search,
                    request.question,
                    request.language,
                    min(request.top_k, self.settings.answer_limit),
                )
            except Exception as error:  # Qdrant exposes multiple transport exceptions.
                last_error = error
                if attempt == 0:
                    await asyncio.sleep(0.025)
        raise RuntimeError("Vector retrieval failed after a retry.") from last_error

    @staticmethod
    def _abstain(
        *,
        request: QueryRequest,
        trace_id: str,
        transcript: str | None,
        reason: str,
        category: str | None,
        stt_ms: float,
        guard_ms: float,
        total_ms: float,
        retrieval_ms: float = 0.0,
        generation_ms: float = 0.0,
        verification_ms: float = 0.0,
        confidence: float = 0.0,
        hits: list[RetrievedHit] | None = None,
    ) -> QueryResponse:
        return QueryResponse(
            trace_id=trace_id,
            transcript=transcript,
            answer="I do not have enough grounded evidence to answer that safely.",
            grounded=False,
            abstained=True,
            confidence=confidence,
            mode=request.mode,
            evidence=[hit.evidence for hit in (hits or [])],
            latency_ms=LatencyBreakdown(
                stt=stt_ms,
                guardrail=guard_ms,
                retrieval=retrieval_ms,
                generation=generation_ms,
                verification=verification_ms,
                total=total_ms + stt_ms,
            ),
            guardrail_reason=f"{category}: {reason}" if category else reason,
        )
