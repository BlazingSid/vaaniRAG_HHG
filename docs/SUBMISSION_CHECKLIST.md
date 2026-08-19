# HH Goa 2026 Task 2 submission checklist

Deadline from the task PDF: **22 August 2026, 11:59 PM**. Submit early enough to test every
public link while signed out.

## Technical completion

- [x] Voice capture in the live UI.
- [x] Sarvam Saaras v4 speech-to-text integration.
- [x] AI4Bharat MSMARCO-XI ingestion path.
- [x] Four non-naive chunking strategies.
- [x] Qdrant dense + BM25 retrieval with reciprocal-rank fusion.
- [x] Fast grounded path and optional Sarvam 105B synthesis.
- [x] Prompt-injection, unsafe-input, low-confidence, and grounding checks.
- [x] Structured retries, fallbacks, trace IDs, and per-stage timing.
- [x] Reproducible P50/P70/P100 benchmark harness.
- [ ] Ingest the final production index.
- [ ] Run and archive the real production text and voice benchmark JSON.
- [ ] Enter measured numbers in `LATENCY_AND_EVALUATION.md` and the process video.

## Links and form

- [ ] Push this repository to the team’s GitHub organization or public account.
- [ ] Add setup instructions, license choice, final benchmark JSON, and team names.
- [ ] Configure the production API and Sarvam secret.
- [ ] Verify the live site uses the production backend, not `verified demo index`.
- [ ] Make the competition demo public.
- [ ] Open the live URL in a signed-out browser and test microphone permission.
- [ ] Confirm the GitHub URL is public or accessible to judges.
- [ ] Complete every required field in the official Google form.
- [ ] Submit GitHub, live, process video, and demo video URLs.
- [ ] Save a timestamped receipt after form submission.

## Required videos and social posts

- [ ] Record the 90-second team/process video using `VIDEO_SCRIPTS.md`.
- [ ] Record the product demo video.
- [ ] Every team member uploads **both videos** to Instagram, X, or LinkedIn.
- [ ] Every post includes **#RAGInGoa** exactly.
- [ ] At least one Instagram post is public.
- [ ] Copy every team member’s post URL into shared submission notes.
- [ ] Check the public Instagram post while signed out.

## Final 30-minute gate

- [ ] No API key appears in Git history, screenshots, videos, or client JavaScript.
- [ ] `/healthz` is healthy and Qdrant collection count is non-zero.
- [ ] One English voice query succeeds.
- [ ] One Marathi voice query succeeds.
- [ ] One weak/off-topic query abstains.
- [ ] The injection sample is blocked.
- [ ] Evidence and query ID display correctly.
- [ ] Benchmark JSON matches the numbers spoken in the video.
- [ ] URLs use HTTPS and do not require the team’s login.
- [ ] Submit before **22 August 2026, 11:59 PM**, not at the last minute.
