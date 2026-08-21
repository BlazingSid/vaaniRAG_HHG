
from __future__ import annotations
from fastapi.middleware.cors import CORSMiddleware
import time
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Settings, get_settings
from .generation import SarvamGroundedGenerator
from .harness import QueryHarness
from .retrieval import HybridRetriever
from .sarvam import SarvamSpeechClient, SpeechServiceError
from .schemas import HealthResponse, QueryRequest, QueryResponse
from contextlib import asynccontextmanager


settings = get_settings()
print("DEBUG SARVAM:", bool(settings.sarvam_api_key))
print("DEBUG TOKEN:", bool(settings.api_bearer_token))
retriever = HybridRetriever(settings)
speech = SarvamSpeechClient(settings)
generator = SarvamGroundedGenerator(settings)
harness = QueryHarness(settings, retriever, generator)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await speech.close()


app = FastAPI(
    title="VaaniRAG API",
    version="1.0.0",
    description="Guarded hybrid retrieval over ai4bharat/MSMARCO-XI.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer_scheme = HTTPBearer(auto_error=False)

def require_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    if not settings.api_bearer_token:
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    expected = settings.api_bearer_token.get_secret_value()

    if credentials.scheme.lower() != "bearer" or credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )


@app.get("/healthz", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        vector_ready = retriever.ready()
    except Exception:
        vector_ready = False
    return HealthResponse(
        status="ok" if vector_ready else "degraded",
        collection=settings.qdrant_collection,
        vector_store_ready=vector_ready,
        sarvam_ready=speech.ready,
    )


@app.post(
    "/v1/query",
    response_model=QueryResponse,
    dependencies=[Depends(require_token)],
)
async def query(request: QueryRequest) -> QueryResponse:
    try:
        return await harness.run(request)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@app.post(
    "/v1/voice",
    response_model=QueryResponse,
    dependencies=[Depends(require_token)],
)
async def voice_query(
    audio: UploadFile = File(...),
    language: str = Form("en-IN"),
    mode: str = Form("fast"),
) -> QueryResponse:
    media_type = (audio.content_type or "").split(";", maxsplit=1)[0].lower()
    if media_type not in {
        "audio/webm",
        "audio/ogg",
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp4",
        "audio/aac",
        "audio/flac",
        "audio/opus",
        "audio/x-m4a",
    }:
        raise HTTPException(status_code=415, detail="Unsupported audio content type.")
    body = await audio.read()
    if len(body) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio files must be at most 10 MB.")

    started = time.perf_counter_ns()
    try:
        transcript = await speech.transcribe(
            body,
            filename=audio.filename or "question.webm",
            content_type=media_type or "audio/webm",
            language=language,
        )
    except SpeechServiceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    stt_ms = (time.perf_counter_ns() - started) / 1_000_000

    try:
        request = QueryRequest(question=transcript.text, language=language, mode=mode)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return await harness.run(request, transcript=transcript.text, stt_ms=stt_ms)
