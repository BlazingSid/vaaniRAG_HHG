#!/usr/bin/env python3
"""Stream MSMARCO-XI records, create multi-view chunks, and upload them to Qdrant."""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

from datasets import load_dataset
from qdrant_client import QdrantClient, models

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.chunking import make_chunks  # noqa: E402
from app.config import get_settings  # noqa: E402


DATASET = "ai4bharat/MSMARCO-XI"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", default="mr", help="MSMARCO-XI config, e.g. mr or hi")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--limit", type=int, default=0, help="0 streams the complete split")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--include-negatives", action="store_true")
    parser.add_argument("--skip-english", action="store_true")
    parser.add_argument("--recreate", action="store_true")
    return parser.parse_args()


def ensure_collection(client: QdrantClient, recreate: bool) -> None:
    settings = get_settings()
    exists = client.collection_exists(settings.qdrant_collection)
    if exists and recreate:
        client.delete_collection(settings.qdrant_collection)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config={
                "dense": models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF,
                )
            },
            on_disk_payload=True,
        )
        client.create_payload_index(
            settings.qdrant_collection,
            field_name="locale",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )


def point_stream(records, language: str, include_negatives: bool, index_english: bool):
    settings = get_settings()
    for record in records:
        for chunk in make_chunks(
            record,
            language,
            include_negatives=include_negatives,
            index_english=index_english,
        ):
            yield models.PointStruct(
                id=chunk.id,
                vector={
                    "dense": models.Document(text=chunk.text, model=settings.dense_model),
                    "sparse": models.Document(text=chunk.text, model=settings.sparse_model),
                },
                payload=chunk.payload(),
            )


def main() -> None:
    args = parse_args()
    settings = get_settings()
    key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=key,
        timeout=60,
        prefer_grpc=settings.prefer_grpc,
    )
    ensure_collection(client, args.recreate)

    data_file = f"{args.split}/marval.parquet" if args.split == "validation" else f"{args.split}/martrain.parquet"
    records = load_dataset(
        DATASET,
        data_files=data_file,
        split="train",
        streaming=True,
    )

    if args.limit:
        records = itertools.islice(records, args.limit)

    client.upload_points(
        collection_name=settings.qdrant_collection,
        points=point_stream(
            records,
            args.language,
            args.include_negatives,
            not args.skip_english,
        ),
        batch_size=args.batch_size,
        parallel=2,
        wait=True,
    )
    count = client.count(settings.qdrant_collection, exact=True).count
    print(f"Indexed {count:,} multi-view chunks in {settings.qdrant_collection}.")


if __name__ == "__main__":
    main()
