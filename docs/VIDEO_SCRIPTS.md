# Video scripts

Replace bracketed fields before recording. Keep browser zoom large enough to read the
transcript, evidence, and timings. Never show `.env`, dashboards, keys, or private URLs.

## Team and process video — 90 seconds

| Time | Visual | Script |
|---:|---|---|
| 0–10s | Team on camera | “We are [TEAM NAME]: [NAMES AND ROLES]. We built VaaniRAG for HH Goa 2026.” |
| 10–25s | Architecture section | “A spoken English or Marathi question is transcribed by Sarvam Saaras v4, screened, and sent to a hybrid Qdrant index over AI4Bharat MSMARCO-XI.” |
| 25–42s | Chunking table or ingestion code | “We avoided naive fixed-size chunks. Each selected passage becomes an atomic passage, overlapping sentence window, parent-child view, and query-answer anchor, with stable IDs and locale filtering.” |
| 42–58s | Response with evidence | “Dense multilingual vectors and BM25 are fused with reciprocal-rank fusion. The fast path returns the dataset answer and cites the retrieved passage.” |
| 58–72s | Guardrail examples | “Injection and unsafe requests are blocked. Weak retrieval or unsupported answers cause an explicit abstention. Qdrant, STT, and generation failures have bounded recovery.” |
| 72–84s | Real benchmark JSON | “Across [N] production [PATH] requests, measured wall latency was P50 [X] ms, P70 [Y] ms, and P100 [Z] ms. These are warm-run, nearest-rank numbers.” |
| 84–90s | Team on camera | “The live demo and source are linked in our submission. #RAGInGoa” |

## Product demo video — 90 seconds

| Time | Action | Narration |
|---:|---|---|
| 0–8s | Open public live URL | “This is VaaniRAG, our live voice-enabled RAG system.” |
| 8–25s | Select Marathi, speak an answerable query | “I’ll ask in Marathi. Sarvam transcribes the audio, then the full guarded retrieval path runs.” |
| 25–40s | Show answer, evidence, trace, latency | “The answer is grounded in MSMARCO-XI. The UI exposes evidence, confidence, mode, and stage timings.” |
| 40–53s | Ask a paraphrase in English | “Hybrid dense and sparse retrieval handles a paraphrase across the multilingual index.” |
| 53–66s | Submit an off-topic query | “When the indexed evidence is weak, the system abstains instead of guessing.” |
| 66–76s | Submit the injection sample | “Prompt injection is stopped before retrieval.” |
| 76–86s | Open benchmark report | “The committed benchmark preserves raw samples and measured P50, P70, and P100.” |
| 86–90s | Return to product | “VaaniRAG: ask the dataset out loud. #RAGInGoa” |

## Recording checklist

- Use the final production build, not a local URL.
- Keep the process video at 90 seconds.
- Include spoken team names and roles in the process video.
- Use real microphone input for the voice demo.
- Show an answer, source evidence, one abstention, and the measured report.
- Add captions, verify audio, and remove notification pop-ups.
- Export 1080p H.264 and watch the exported file end-to-end before upload.
