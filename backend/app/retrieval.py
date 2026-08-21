from __future__ import annotations

import time
from dataclasses import dataclass

from qdrant_client import QdrantClient, models
from qdrant_client.models import ScoredPoint

from .config import Settings
from .guardrails import retrieval_confidence
from .schemas import Evidence


@dataclass(frozen=True)
class RetrievedHit:
    evidence: Evidence
    answer: str
    confidence: float
    parent_context: str


class HybridRetriever:
    """Dense + BM25 retrieval fused with reciprocal-rank fusion in Qdrant."""

    def __init__(self, settings: Settings):
        api_key = (
            settings.qdrant_api_key.get_secret_value()
            if settings.qdrant_api_key
            else None
        )

        self.settings = settings

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=api_key,
            timeout=settings.qdrant_timeout_seconds,
            prefer_grpc=settings.prefer_grpc,
            check_compatibility=False,
        )

    def ready(self) -> bool:
        return self.client.collection_exists(
            self.settings.qdrant_collection
        )

    def search(
        self,
        question: str,
        language: str,
        limit: int,
    ) -> list[RetrievedHit]:

        locale = language.split("-", maxsplit=1)[0]

        locale_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="locale",
                    match=models.MatchValue(value=locale),
                )
            ]
        )

        prefetch_limit = max(
            limit,
            self.settings.prefetch_limit,
        )

        # Temporary latency profiling
        started = time.perf_counter()

        result = self.client.query_points(
            collection_name=self.settings.qdrant_collection,
            prefetch=[
                models.Prefetch(
                    query=models.Document(
                        text=question,
                        model=self.settings.dense_model,
                    ),
                    using="dense",
                    filter=locale_filter,
                    limit=prefetch_limit,
                ),
                models.Prefetch(
                    query=models.Document(
                        text=question,
                        model=self.settings.sparse_model,
                    ),
                    using="sparse",
                    filter=locale_filter,
                    limit=prefetch_limit,
                ),
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            limit=limit,
            with_payload=True,
        )

        elapsed_ms = (
            time.perf_counter() - started
        ) * 1000

        print(
            f"[RETRIEVAL DEBUG] "
            f"Qdrant: {elapsed_ms:.2f} ms"
        )

        return [
            self._to_hit(question, point)
            for point in result.points
        ]

    @staticmethod
    def _to_hit(
        question: str,
        point: ScoredPoint,
    ) -> RetrievedHit:

        payload = point.payload or {}

        text = str(
            payload.get("document")
            or payload.get("text")
            or ""
        )

        score = float(point.score or 0.0)

        evidence = Evidence(
            id=str(point.id),
            text=text,
            score=score,
            strategy=str(
                payload.get("strategy")
                or "unknown"
            ),
            query_id=(
                str(payload["query_id"])
                if payload.get("query_id")
                else None
            ),
            source=str(
                payload.get("source")
                or "ai4bharat/MSMARCO-XI"
            ),
        )

        return RetrievedHit(
            evidence=evidence,
            answer=str(
                payload.get("answer") or ""
            ),
            confidence=retrieval_confidence(
                question,
                text,
                score,
            ),
            parent_context=str(
                payload.get("parent_context")
                or text
            ),
        )