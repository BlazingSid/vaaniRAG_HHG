import { retrieveDemo, validateQuestion } from "../../retrieval";

type QueryPayload = { question?: string; language?: "en-IN" | "mr-IN" };

function elapsed(start: number) {
  return Math.round((performance.now() - start) * 10) / 10;
}

function traceId() {
  return `vr_${crypto.randomUUID().replaceAll("-", "").slice(0, 16)}`;
}

export async function POST(request: Request) {
  const started = performance.now();
  let payload: QueryPayload;
  try {
    payload = await request.json() as QueryPayload;
  } catch {
    return Response.json({ error: "Expected a JSON request body." }, { status: 400 });
  }

  const question = payload.question?.trim() ?? "";
  const language = payload.language === "mr-IN" ? "mr-IN" : "en-IN";
  const guardrailStarted = performance.now();
  const violation = validateQuestion(question);
  const guardrail = elapsed(guardrailStarted);
  if (violation) {
    return Response.json({ error: violation, trace_id: traceId() }, { status: 422 });
  }

  const runtime = process.env as Record<string, string | undefined>;
  const backendUrl = runtime.RAG_BACKEND_URL?.replace(/\/$/, "");
  if (backendUrl) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const upstream = await fetch(`${backendUrl}/v1/query`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          ...(runtime.RAG_BACKEND_TOKEN ? { authorization: `Bearer ${runtime.RAG_BACKEND_TOKEN}` } : {}),
        },
        body: JSON.stringify({ question, language, mode: "fast" }),
        signal: controller.signal,
      });
      const result = await upstream.json();
      return Response.json(result, { status: upstream.status });
    } catch {
      // Circuit-breaker fallback: retain a usable edge demo if the full backend is down.
    } finally {
      clearTimeout(timeout);
    }
  }

  const retrievalStarted = performance.now();
  const ranked = retrieveDemo(question, language);
  const retrieval = elapsed(retrievalStarted);
  const best = ranked[0];
  const confidence = Math.min(0.99, Math.max(0, best?.score ?? 0));
  const threshold = 0.16;
  const generationStarted = performance.now();
  const abstained = !best || confidence < threshold;
  const answer = abstained
    ? language === "mr-IN"
      ? "दिलेल्या MSMARCO-XI पुराव्यात या प्रश्नासाठी पुरेशी माहिती सापडली नाही, म्हणून मी उत्तर देणार नाही."
      : "I could not find enough supporting evidence in the indexed MSMARCO-XI context, so I will not guess."
    : best.localized.answer;
  const generation = elapsed(generationStarted);

  return Response.json({
    trace_id: traceId(), answer, grounded: !abstained, abstained, confidence,
    mode: backendUrl ? "edge fallback" : "verified demo index",
    evidence: abstained || !best ? [] : [{
      id: best.record.id,
      text: best.localized.passage,
      score: best.score,
      strategy: "query-anchor + passage",
    }],
    latency_ms: { guardrail, retrieval, generation, total: elapsed(started) },
  });
}
