# API contract

## `GET /healthz`

Unauthenticated readiness signal. `degraded` means Qdrant is unavailable or the collection
does not exist. `sarvam_ready` indicates whether a key is configured; it makes no billable
upstream request.

## `POST /v1/query`

```json
{
  "question": "कॉर्पोरेशन म्हणजे काय?",
  "language": "mr-IN",
  "mode": "fast",
  "top_k": 5
}
```

`mode` is `fast` or `generative`. Generative mode is honored only when
`ENABLE_GENERATIVE_MODE=true` and the request is still inside the configured query deadline;
otherwise the service returns the grounded dataset answer.

## `POST /v1/voice`

| Multipart field | Required | Value |
|---|---:|---|
| `audio` | yes | WebM, OGG, WAV, MP3, or MP4; at most 10 MB |
| `language` | no | BCP-47 code such as `mr-IN`; default `en-IN` |
| `mode` | no | `fast` or `generative`; default `fast` |

The response shape is identical to `/v1/query` and adds `transcript` plus non-zero `stt`
latency.

## Successful or abstained response

```json
{
  "trace_id": "c04d...",
  "transcript": null,
  "answer": "A corporation is ...",
  "grounded": true,
  "abstained": false,
  "confidence": 0.76,
  "mode": "fast",
  "evidence": [{
    "id": "...",
    "text": "...",
    "score": 0.72,
    "strategy": "query_answer_anchor",
    "query_id": "233826",
    "source": "ai4bharat/MSMARCO-XI"
  }],
  "latency_ms": {
    "stt": 0,
    "guardrail": 0.1,
    "retrieval": 34.2,
    "generation": 0,
    "verification": 0.1,
    "total": 34.7
  },
  "guardrail_reason": null
}
```

An abstention is a normal HTTP 200 result with `grounded=false`, `abstained=true`, and a
category prefix in `guardrail_reason`. Infrastructure failures return 503; malformed input
returns 4xx; unsupported media returns 415.
