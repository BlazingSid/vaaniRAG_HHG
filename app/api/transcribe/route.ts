const allowedLanguages = new Set(["en-IN", "mr-IN"]);

export async function POST(request: Request) {
  const runtime = process.env as Record<string, string | undefined>;
  const apiKey = runtime.SARVAM_API_KEY;
  if (!apiKey) {
    return Response.json({
      error: "Voice input is ready but the server's Sarvam API key has not been configured yet. Use a sample text question for now.",
    }, { status: 503 });
  }

  const form = await request.formData();
  const audio = form.get("audio");
  const requestedLanguage = String(form.get("language") || "en-IN");
  const language = allowedLanguages.has(requestedLanguage) ? requestedLanguage : "en-IN";
  if (!(audio instanceof File) || audio.size === 0) {
    return Response.json({ error: "A non-empty audio file is required." }, { status: 400 });
  }
  if (audio.size > 8 * 1024 * 1024) {
    return Response.json({ error: "Keep voice questions below 8 MB and 30 seconds." }, { status: 413 });
  }

  const upstreamForm = new FormData();
  upstreamForm.append("file", audio, audio.name || "question.webm");
  upstreamForm.append("model", "saaras:v4");
  upstreamForm.append("language_code", language);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch("https://api.sarvam.ai/speech-to-text", {
      method: "POST",
      headers: { "api-subscription-key": apiKey },
      body: upstreamForm,
      signal: controller.signal,
    });
    const payload = await response.json() as { transcript?: string; error?: { message?: string } };
    if (!response.ok || !payload.transcript) {
      return Response.json({ error: payload.error?.message || "Sarvam could not transcribe that audio." }, { status: response.status || 502 });
    }
    return Response.json({ transcript: payload.transcript, language });
  } catch {
    return Response.json({ error: "Speech transcription timed out. Please try once more." }, { status: 504 });
  } finally {
    clearTimeout(timeout);
  }
}
