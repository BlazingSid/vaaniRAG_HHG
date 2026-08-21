# SynroxRAG System

> Voice-enabled multilingual RAG system built for the HackerHouse Goa challenge.

SynroxRAG is a voice-first Retrieval-Augmented Generation system designed to answer questions from a large multilingual knowledge base while prioritizing **grounded answers, low retrieval latency, and safe abstention**.

The system accepts a spoken question, converts it to text, retrieves relevant evidence using hybrid search, evaluates the grounding confidence, and returns an answer only when the retrieved evidence is strong enough.

---

## Why SynroxRAG?

Traditional voice assistants can produce convincing answers even when they do not actually have evidence for them.

SynroxRAG takes a different approach:

**If the system cannot find strong enough evidence, it refuses to guess.**

This makes the system particularly useful for knowledge-intensive applications where hallucinated answers are worse than no answer.

---

## System Architecture

```text
                    ┌──────────────────┐
                    │    User Voice    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Sarvam STT     │
                    │ Speech → Text    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Guardrails    │
                    │ Query validation │
                    └────────┬─────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │       Hybrid Retrieval       │
              │                              │
              │  Dense Search + BM25 Search │
              │             ↓                │
              │          RRF Fusion          │
              └──────────────┬───────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Confidence     │
                    │    Scoring       │
                    └────────┬─────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
              Strong evidence      Weak evidence
                   │                   │
                   ▼                   ▼
              Grounded Answer       Abstain
```

---

## Production Deployment Architecture (₹0 Budget / 24/7 Public)

The system is deployed permanently on free-tier cloud infrastructure:

1. **Vector Database**: **Qdrant Cloud (Free Tier)**
   - Collection: `msmarco_xi_multiview_v1`
   - Indexed Points: **22,414 points** (Dense 384-d + BM25 Sparse + Payload + Locale Keyword Index)
   - High availability, managed cloud cluster.

2. **Backend API**: **Dockerized FastAPI (Hugging Face Spaces / Render / Koyeb)**
   - Dockerfile: `backend/Dockerfile`
   - Port: `$PORT` (7860/8000)
   - Endpoints:
     - `GET /healthz` - Health status and vector store check
     - `POST /v1/query` - Guarded hybrid retrieval with RRF fusion
     - `POST /v1/voice` - Voice-to-search pipeline

3. **Frontend Client**: **React 19 / vinext / Next.js (Vercel / Cloudflare Pages)**
   - Public voice search interface with Sarvam Saaras v4 STT integration
   - Edge proxying to FastAPI backend with graceful fallback

---

## Environment Variables Reference

### Backend Service
| Variable | Description |
|---|---|
| `QDRANT_URL` | Qdrant Cloud cluster endpoint |
| `QDRANT_API_KEY` | Qdrant Cloud API key |
| `QDRANT_COLLECTION` | `msmarco_xi_multiview_v1` |
| `SARVAM_API_KEY` | Sarvam AI API key |
| `API_BEARER_TOKEN` | Bearer token for authenticating backend requests |
| `QUERY_DEADLINE_MS` | `200.0` |
| `MIN_GROUNDING_CONFIDENCE` | `0.30` |
| `ENABLE_GENERATIVE_MODE` | `false` |

### Frontend Service
| Variable | Description |
|---|---|
| `RAG_BACKEND_URL` | Public HTTPS URL of the deployed FastAPI backend |
| `RAG_BACKEND_TOKEN` | Bearer token matching `API_BEARER_TOKEN` |
| `SARVAM_API_KEY` | Sarvam AI API key for speech transcription |

---

## Reproducing the Deployment

1. **Deploy Backend**:
   - Link GitHub repository `BlazingSid/vaaniRAG_HHG` to Render or Hugging Face Spaces (Docker Space).
   - Set Dockerfile Path: `backend/Dockerfile` and Context: `backend`.
   - Set the Backend environment variables listed above.

2. **Deploy Frontend**:
   - Link GitHub repository `BlazingSid/vaaniRAG_HHG` to Vercel or Cloudflare Pages.
   - Set Build Command: `npx vinext build` or standard Next.js build.
   - Set the Frontend environment variables listed above.