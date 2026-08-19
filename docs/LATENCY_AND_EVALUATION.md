# Latency and evaluation protocol

## Claim boundary

No production latency result is included by default. It would be misleading to claim
sub-200 ms without running the provisioned Qdrant collection, Sarvam account, deployment
region, and real voice fixtures. The benchmark command produces the submission evidence
once those resources are configured.

Report these paths separately:

1. **Fast text** — guardrail + hybrid retrieval + gold-answer release + verification.
2. **Fast voice** — Sarvam STT + the complete fast text path.
3. **Generative voice** — Sarvam STT + retrieval + Sarvam 105B + verification.

Only call a path “under 200 ms” if its measured P100 is under 200 ms. If P50 is below the
target but P100 is not, state both values plainly.

## Reproducible procedure

1. Deploy API and Qdrant in the same region; run ingestion to completion.
2. Confirm `/healthz` reports `vector_store_ready=true`.
3. Use at least 30 answerable and 10 adversarial/unanswerable queries across English and
   Marathi. Record dataset query IDs for answerable cases.
4. Record one natural voice fixture per answerable question at 16 kHz or better, under 30
   seconds. Do not use synthesized audio as the only evaluation.
5. Run two warmups per case and exclude them.
6. Run at least ten measured repetitions per case.
7. Save the exact JSON output, deployment commit, region, date, index size, and config.
8. Manually grade answer correctness and evidence support; do not use latency alone.

The runner uses wall-clock time around the HTTP request and independently records server
stages. P50/P70/P100 use nearest-rank. P100 is the observed maximum, not an extrapolated
tail estimate.

## Results table to complete after production measurement

| Path | N | P50 wall | P70 wall | P100 wall | Grounded accuracy | Safe abstention | Date/region |
|---|---:|---:|---:|---:|---:|---:|---|
| Fast text | — | — | — | — | — | — | — |
| Fast voice | — | — | — | — | — | — | — |
| Generative voice | — | — | — | — | — | — | — |

## Functional acceptance matrix

| Case | Expected behavior |
|---|---|
| Exact answerable query | Gold answer, evidence, `grounded=true` |
| Paraphrased answerable query | Supported answer above threshold |
| Off-topic current event | Abstain |
| Prompt injection | Block before retrieval |
| Unsafe procedural request | Block before retrieval |
| Weak retrieval | Abstain with `low_confidence` |
| Unsupported generated answer | Abstain with `ungrounded_answer` |
| Qdrant transient error | Retry once, then 503 |
| Sarvam transient error | Retry up to three attempts |
| Generator failure | Return fast grounded answer |

Store the unedited `benchmark_results.json` and generated CSV with the submission evidence
so reviewers can recalculate every percentile from the raw samples.
