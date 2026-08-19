#!/usr/bin/env python3
"""Benchmark text or voice requests and report nearest-rank P50/P70/P100."""

from __future__ import annotations

import argparse
import csv
import json
import math
import mimetypes
import statistics
import time
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--manifest", default="benchmark_queries.jsonl")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--token", default=None)
    parser.add_argument("--output", default="benchmark_results.json")
    return parser.parse_args()


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil((percent / 100) * len(ordered)))
    return ordered[rank - 1]


def load_manifest(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not row.get("question") and not row.get("audio"):
            raise ValueError(f"Manifest line {line_number} needs question or audio.")
        rows.append(row)
    return rows


def request_once(client, base_url: str, row: dict) -> dict:
    started = time.perf_counter_ns()
    if row.get("audio"):
        audio_path = Path(row["audio"]).expanduser().resolve()
        mime = mimetypes.guess_type(audio_path.name)[0] or "audio/webm"
        with audio_path.open("rb") as stream:
            response = client.post(
                f"{base_url.rstrip('/')}/v1/voice",
                data={
                    "language": row.get("language", "en-IN"),
                    "mode": row.get("mode", "fast"),
                },
                files={"audio": (audio_path.name, stream, mime)},
            )
    else:
        response = client.post(
            f"{base_url.rstrip('/')}/v1/query",
            json={
                "question": row["question"],
                "language": row.get("language", "en-IN"),
                "mode": row.get("mode", "fast"),
            },
        )
    wall_ms = (time.perf_counter_ns() - started) / 1_000_000
    response.raise_for_status()
    payload = response.json()
    return {
        "question": row.get("question"),
        "audio": row.get("audio"),
        "language": row.get("language", "en-IN"),
        "wall_ms": wall_ms,
        "latency_ms": payload.get("latency_ms", {}),
        "grounded": bool(payload.get("grounded")),
        "abstained": bool(payload.get("abstained")),
        "trace_id": payload.get("trace_id"),
    }


def main() -> None:
    import httpx

    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    rows = load_manifest(manifest_path)
    headers = {"authorization": f"Bearer {args.token}"} if args.token else {}
    samples: list[dict] = []

    with httpx.Client(headers=headers, timeout=30) as client:
        for row in rows:
            for _ in range(args.warmup):
                request_once(client, args.url, row)
            for _ in range(args.runs):
                samples.append(request_once(client, args.url, row))

    metrics = ["wall_ms", "stt", "guardrail", "retrieval", "generation", "verification", "total"]
    summary: dict[str, dict[str, float]] = {}
    for metric in metrics:
        values = [
            float(sample["wall_ms"] if metric == "wall_ms" else sample["latency_ms"].get(metric, 0))
            for sample in samples
        ]
        summary[metric] = {
            "p50": round(percentile(values, 50), 3),
            "p70": round(percentile(values, 70), 3),
            "p100": round(percentile(values, 100), 3),
            "mean": round(statistics.fmean(values), 3),
        }

    report = {
        "method": "nearest-rank percentiles; warmups excluded",
        "endpoint": args.url,
        "manifest": str(manifest_path),
        "sample_count": len(samples),
        "grounded_rate": sum(sample["grounded"] for sample in samples) / len(samples),
        "abstention_rate": sum(sample["abstained"] for sample in samples) / len(samples),
        "summary_ms": summary,
        "samples": samples,
    }
    output = Path(args.output).resolve()
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_output = output.with_suffix(".csv")
    with csv_output.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = [
            "trace_id", "question", "audio", "language", "grounded", "abstained",
            "wall_ms", "stt", "guardrail", "retrieval", "generation", "verification", "total",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for sample in samples:
            writer.writerow({
                **{key: sample.get(key) for key in fieldnames},
                **sample["latency_ms"],
            })
    print(json.dumps(report["summary_ms"], indent=2))
    print(f"Saved {len(samples)} measured requests to {output} and {csv_output}.")


if __name__ == "__main__":
    main()
