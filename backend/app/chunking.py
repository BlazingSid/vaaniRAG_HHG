import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Iterable


NAMESPACE = uuid.UUID("1ac45cf3-487b-4591-bdd6-7d2146f37985")


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    query_id: str
    query: str
    answer: str
    locale: str
    dataset_language: str
    query_type: str
    strategy: str
    passage_index: int
    selected: bool
    parent_context: str

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value["source"] = "ai4bharat/MSMARCO-XI"
        value["document"] = self.text
        return value


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?।])\s+|\n+", text.strip())
    return [piece.strip() for piece in pieces if piece.strip()]


def sentence_windows(text: str, size: int = 2, overlap: int = 1) -> list[str]:
    sentences = split_sentences(text)
    if len(sentences) <= size:
        return [text.strip()] if text.strip() else []
    step = max(1, size - overlap)
    return [" ".join(sentences[index:index + size]) for index in range(0, len(sentences), step)]


def stable_id(*parts: object) -> str:
    return str(uuid.uuid5(NAMESPACE, ":".join(str(part) for part in parts)))


def _variants(record: dict[str, Any], dataset_language: str, index_english: bool):
    passages = record.get("passages") or {}
    yield (
        dataset_language,
        str(record.get("query") or ""),
        str(record.get("Answer") or ""),
        list(passages.get("Translated_passages") or []),
    )
    if index_english:
        yield (
            "en",
            str(record.get("Eng_Query") or ""),
            str(record.get("Eng_Answer") or ""),
            list(passages.get("English_passages") or []),
        )


def make_chunks(
    record: dict[str, Any],
    dataset_language: str,
    *,
    include_negatives: bool = False,
    index_english: bool = True,
) -> Iterable[Chunk]:
    query_id = str(record.get("query_id") or "unknown")
    query_type = str(record.get("query_type") or "UNKNOWN")
    selected_flags = list((record.get("passages") or {}).get("is_selected") or [])

    for locale, query, answer, passages in _variants(record, dataset_language, index_english):
        for passage_index, parent in enumerate(passages):
            parent = str(parent or "").strip()
            selected = bool(selected_flags[passage_index]) if passage_index < len(selected_flags) else False
            if not parent or (not include_negatives and not selected):
                continue

            common = dict(
                query_id=query_id, query=query, answer=answer, locale=locale,
                dataset_language=dataset_language, query_type=query_type,
                passage_index=passage_index, selected=selected, parent_context=parent,
            )

            yield Chunk(
                id=stable_id(query_id, locale, passage_index, "atomic", 0),
                text=parent, strategy="atomic_passage", **common,
            )

            windows = sentence_windows(parent, size=2, overlap=1)
            for window_index, window in enumerate(windows):
                yield Chunk(
                    id=stable_id(query_id, locale, passage_index, "window", window_index),
                    text=window, strategy="sentence_window", **common,
                )
                yield Chunk(
                    id=stable_id(query_id, locale, passage_index, "child", window_index),
                    text=window, strategy="parent_child", **common,
                )

            if selected and query:
                anchor = f"Question: {query}\nAnswer: {answer}\nEvidence: {parent}".strip()
                yield Chunk(
                    id=stable_id(query_id, locale, passage_index, "qa", 0),
                    text=anchor, strategy="query_answer_anchor", **common,
                )
