"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type Language = "en-IN" | "mr-IN";

type Evidence = {
  id: string;
  text: string;
  score: number;
  strategy: string;
};

type QueryResult = {
  trace_id: string;
  transcript?: string;
  answer: string;
  grounded: boolean;
  abstained: boolean;
  confidence: number;
  mode: string;
  evidence: Evidence[];
  latency_ms: {
    guardrail: number;
    retrieval: number;
    generation: number;
    total: number;
  };
};

const samples: Record<Language, string[]> = {
  "en-IN": [
    "How fast does an eagle travel?",
    "What is a corporation?",
    "How long does cantaloupe take to mature?",
  ],
  "mr-IN": [
    "गरुड किती वेगाने प्रवास करतो?",
    "कॉर्पोरेशन म्हणजे काय?",
    "कॅन्टालूप परिपक्व होण्यासाठी किती वेळ लागतो?",
  ],
};

const pipelineStages = [
  ["Voice", "Sarvam Saaras"],
  ["Index", "4-way chunks"],
  ["Retrieve", "Hybrid + RRF"],
  ["Answer", "Evidence only"],
];

function milliseconds(value?: number) {
  return typeof value === "number" ? `${value.toFixed(1)} ms` : "-";
}

export default function Home() {
  const [language, setLanguage] = useState<Language>("en-IN");
  const [question, setQuestion] = useState(samples["en-IN"][0]);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    return () => streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  async function ask(nextQuestion = question, transcript?: string) {
    const cleaned = nextQuestion.trim();
    if (!cleaned || loading) return;

    setLoading(true);
    setNotice(null);
    setResult(null);

    try {
      const response = await fetch("https://girls-tabs-gave-sensitivity.trycloudflare.com/v1/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer change-me",
        },
        body: JSON.stringify({
          question: cleaned,
          language,
        }),
      });
      const payload = (await response.json()) as QueryResult & { error?: string };
      if (!response.ok) throw new Error(payload.error || "The query could not be processed.");
      setResult({ ...payload, transcript });
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask();
  }

  async function toggleRecording() {
    if (recording) {
      recorderRef.current?.stop();
      return;
    }

    setNotice(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];
      const preferredType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType: preferredType });
      recorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data.size) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        setRecording(false);
        stream.getTracks().forEach((track) => track.stop());
        const audio = new Blob(chunksRef.current, { type: "audio/webm" });
        if (!audio.size) {
          setNotice("No audio was captured. Please try again.");
          return;
        }
        setLoading(true);
        try {
          const form = new FormData();
          form.append("audio", audio, "question.webm");
          form.append("language", language);
          const response = await fetch(
  "https://girls-tabs-gave-sensitivity.trycloudflare.com/v1/query",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer change-me",
    },
    body: JSON.stringify({
      question,
      language: "en-IN",
      mode: "fast",
    }),
  }
);

if (!response.ok) {
  throw new Error(`API request failed: ${response.status}`);
}

const data = await response.json();
          const payload = (await response.json()) as { transcript?: string; error?: string };
          if (!response.ok || !payload.transcript) {
            throw new Error(payload.error || "Speech could not be transcribed.");
          }
          setQuestion(payload.transcript);
          setLoading(false);
          await ask(payload.transcript, payload.transcript);
        } catch (error) {
          setNotice(error instanceof Error ? error.message : "Speech could not be transcribed.");
          setLoading(false);
        }
      };
      recorder.start(200);
      setRecording(true);
    } catch {
      setNotice("Microphone access was blocked. You can still use the text box.");
    }
  }

  function switchLanguage(next: Language) {
    setLanguage(next);
    setQuestion(samples[next][0]);
    setResult(null);
    setNotice(null);
  }

  return (
    <main>
      <nav className="nav-shell" aria-label="Primary navigation">
        <a className="wordmark" href="#top" aria-label="SyNroXRAG System Home">
          <span className="wordmark-logo" aria-hidden="true">S</span>
          <span>SyNroX<span className="slash">/</span>RAG</span>
        </a>
        <div className="nav-meta">
          <span className="status-dot" aria-hidden="true" />
          HH Goa 2026 build
        </div>
        <a className="nav-link" href="#architecture">How it works</a>
        <a className="nav-link" href="#latency">build by @teamsynrox</a>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span>01</span> VOICE-NATIVE <b>•</b> GROUNDED <b> MULTILINGUAL</b></p>
          <h1>
            Synrox<span>RAG</span> System
          </h1>
          <p className="hero-lede">
            Ask anything in your language.
            <br />
            Get grounded answers with evidence, not guesses.
          </p>
        </div>

        <div className="console-wrap">
          <div className="console-topline">
            <div>
              <span className="live-pill"><i /> LIVE PIPELINE</span>
              <span className="index-label">MULTILINGUAL KNOWLEDGE ENGINE</span>
            </div>
            <label className="language-control">
              <span className="sr-only">Question language</span>
              <select value={language} onChange={(event) => switchLanguage(event.target.value as Language)}>
                <option value="en-IN">English</option>
                <option value="mr-IN">मराठी</option>
              </select>
            </label>
          </div>

          <div className="ask-grid">
            <div className="mic-column">
              <div className={`mic-rings ${recording ? "is-recording" : ""}`}>
                <button
                  className="mic-button"
                  type="button"
                  onClick={() => void toggleRecording()}
                  aria-label={recording ? "Stop recording" : "Start voice question"}
                >
                  <span className="mic-icon" aria-hidden="true" />
                </button>
              </div>
              <p className="mic-label">{recording ? "Listening - tap to stop" : "Tap to speak"}</p>
              <p className="mic-hint">Sarvam Saaras v4</p>
            </div>

            <div className="query-column">
              <p className="field-kicker">Or type your question</p>
              <form className="query-form" onSubmit={submit}>
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={2}
                  maxLength={400}
                  aria-label="Question"
                />
                <button disabled={loading || !question.trim()} type="submit">
                  {loading ? "Running" : "Ask"}<span aria-hidden="true">↗</span>
                </button>
              </form>
              <div className="sample-row" aria-label="Sample questions">
                <span>Try</span>
                {samples[language].map((sample) => (
                  <button key={sample} type="button" onClick={() => { setQuestion(sample); void ask(sample); }}>
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {notice && <div className="notice" role="alert"><span>!</span>{notice}</div>}

          {(loading || result) && (
            <section className={`answer-panel ${loading ? "is-loading" : ""}`} aria-live="polite">
              {loading ? (
                <div className="loading-state">
                  <div className="scan-line" />
                  <p>Running the guarded retrieval harness...</p>
                </div>
              ) : result && (
                <>
                  <div className="answer-meta">
                    <span className={result.grounded ? "grounded" : "abstained"}>
                      <i /> {result.grounded ? "Grounded answer" : "Abstained safely"}
                    </span>
                    <span>{Math.round(result.confidence * 100)}% retrieval confidence</span>
                    <span className="answer-mode">{result.mode}</span>
                  </div>
                  {result.transcript && (
                    <p className="transcript"><span>Transcript</span>{result.transcript}</p>
                  )}
                  <p className="answer-text">{result.answer}</p>
                  {result.evidence[0] && (
                    <details className="evidence" open>
                      <summary>Evidence · MSMARCO-XI query {result.evidence[0].id}</summary>
                      <p>{result.evidence[0].text}</p>
                    </details>
                  )}
                  <div className="latency-strip">
                    <div><span>Guardrail</span><b>{milliseconds(result.latency_ms.guardrail)}</b></div>
                    <div><span>Retrieval</span><b>{milliseconds(result.latency_ms.retrieval)}</b></div>
                    <div><span>Compose</span><b>{milliseconds(result.latency_ms.generation)}</b></div>
                    <div className="total-latency"><span>Online total</span><b>{milliseconds(result.latency_ms.total)}</b></div>
                  </div>
                </>
              )}
            </section>
          )}
        </div>

        <div className="pipeline-ribbon" aria-label="Pipeline stages">
          {pipelineStages.map(([label, detail], index) => (
            <div className="pipeline-stage" key={label}>
              <span>0{index + 1}</span>
              <p><b>{label}</b><small>{detail}</small></p>
              {index < pipelineStages.length - 1 && <i aria-hidden="true">→</i>}
            </div>
          ))}
        </div>
      </section>

      <section className="architecture" id="architecture">
        <div className="section-intro">
          <p className="eyebrow"><span>02</span> Built to clear the brief</p>
          <h2>Fast where it counts.<br />Honest everywhere.</h2>
          <p>
            Expensive work happens once during ingestion. The online path stays small,
            measurable, and aggressively guarded.
          </p>
        </div>
        <div className="feature-grid">
          <article className="feature feature-primary">
            <span className="feature-number">01</span>
            <h3>Four views of every passage</h3>
            <p>Atomic passages, sentence windows, parent-child chunks, and metadata-rich query-answer anchors are indexed together.</p>
            <div className="chunk-visual" aria-hidden="true">
              <i className="chunk-a" /><i className="chunk-b" /><i className="chunk-c" /><i className="chunk-d" />
            </div>
          </article>
          <article className="feature">
            <span className="feature-number">02</span>
            <h3>Structured harness</h3>
            <p>Typed inputs, trace IDs, bounded retries, timeouts, circuit breakers, and a deterministic evidence fallback.</p>
            <code>voice → guard → retrieve → verify</code>
          </article>
          <article className="feature">
            <span className="feature-number">03</span>
            <h3>Abstention is a feature</h3>
            <p>Prompt-injection screening, retrieval thresholds, source coverage checks, and no-evidence refusal paths.</p>
            <div className="guard-meter"><span>evidence coverage</span><i><b /></i></div>
          </article>
          <article className="feature feature-metric">
            <span className="feature-number">04</span>
            <h3>Latency, without theatre</h3>
            <p>The benchmark command records every stage and calculates P50, P70, and max across the full test set.</p>
            <div className="metric-placeholder">
              <b>P50</b><span>run benchmark</span><b>P70</b><span>run benchmark</span><b>P100</b><span>run benchmark</span>
            </div>
          </article>
        </div>
      </section>

      <section className="brief-matrix">
        <div>
          <p className="eyebrow"><span>03</span> Requirement matrix</p>
          <h2>Nothing hand-waved.</h2>
        </div>
        <div className="matrix-list">
          {[
            ["Speech-to-text", "Sarvam Saaras v4 REST with WebM voice capture"],
            ["Vector retrieval", "Qdrant HNSW, dense + lexical reciprocal-rank fusion"],
            ["Chunking", "Four strategies with language and query metadata"],
            ["Harness", "Retries, time budgets, tracing, structured contracts"],
            ["Guardrails", "Input, topic, grounding, and abstention layers"],
            ["Analytics", "Per-stage CSV/JSON with P50, P70, P100"],
          ].map(([requirement, implementation], index) => (
            <div className="matrix-row" key={requirement}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <b>{requirement}</b>
              <p>{implementation}</p>
              <i aria-label="implemented">✓</i>
            </div>
          ))}
        </div>
      </section>
      <section className="latency-note" id="latency">
  <div className="latency-note-inner">
    <div className="latency-note-header">
      <span className="latency-note-index">04</span>
      <span className="latency-note-label">TeamSyNroX note</span>
    </div>

    <div className="latency-note-grid">
      <div>
        <h2>
          We didn't hit
          <br />
          <em>200 ms.</em>
        </h2>
      </div>

      <div className="latency-note-copy">
        <p className="latency-note-lede">
          And we're not going to pretend we did.
        </p>

        <p>
          Our target was a sub-200 ms end-to-end voice experience.
          We pushed the retrieval and verification pipeline hard, but
          speech-to-text remained the main latency bottleneck.
        </p>

        <p>
          Across our tests, STT typically landed in the
          <strong> 300–900 ms</strong> range, while retrieval itself
          could respond in only a few milliseconds.
        </p>

        <p>
          That's not the end of the project. It's the measurement that
          tells us where the next round of engineering needs to happen.
        </p>
      </div>
    </div>

    <div className="latency-stats">
      <div>
        <span>Target</span>
        <strong>&lt; 200 ms</strong>
      </div>

      <div>
        <span>STT observed</span>
        <strong>~300–900 ms</strong>
      </div>

      <div>
        <span>Retrieval observed</span>
        <strong>~6–130 ms</strong>
      </div>

      <div className="latency-next">
        <span>Next</span>
        <strong>Optimize the voice path →</strong>
      </div>
    </div>

    <div className="latency-motivation">
      <span>BUILD → MEASURE → LEARN → ITERATE</span>
      <p>
        Every limitation gives us another thing to improve.
        This is version one. We're just getting started.
        Signing off -teamsynrox
      </p>
    </div>
  </div>
</section>

      <footer>
        <a className="wordmark" href="#top"><span className="wordmark-mark">v</span><span>SyNroX<span className="slash">/</span>RAG</span></a>
        <p>Built for HH Goa 2026 · AI4Bharat MSMARCO-XI · <b>#RAGInGoa</b></p>
        <a href="https://huggingface.co/datasets/ai4bharat/MSMARCO-XI" target="_blank" rel="noreferrer">Dataset ↗</a>
      </footer>
    </main>
  );
}
