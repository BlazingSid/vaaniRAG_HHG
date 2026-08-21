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