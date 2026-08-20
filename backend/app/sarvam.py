from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from .config import Settings


class SpeechServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class Transcript:
    text: str
    language_code: str


class SarvamSpeechClient:
    endpoint = "https://api.sarvam.ai/speech-to-text"

    def __init__(self, settings: Settings):
        self.settings = settings

        # Reuse the same HTTP connection between requests.
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=3.0,
                read=settings.sarvam_timeout_seconds,
                write=5.0,
                pool=2.0,
            ),
            limits=httpx.Limits(
                max_connections=10,
                max_keepalive_connections=5,
                keepalive_expiry=30.0,
            ),
            http2=True,
        )

    @property
    def ready(self) -> bool:
        return self.settings.sarvam_api_key is not None

    async def transcribe(
        self,
        audio: bytes,
        *,
        filename: str,
        content_type: str,
        language: str,
    ) -> Transcript:

        if not self.settings.sarvam_api_key:
            raise SpeechServiceError("SARVAM_API_KEY is not configured.")

        if not audio:
            raise SpeechServiceError("The audio file is empty.")

        headers = {
            "api-subscription-key": (
                self.settings.sarvam_api_key.get_secret_value()
            )
        }

        data = {
            "model": self.settings.sarvam_stt_model,
            "language_code": language,
        }

        retryable = {408, 429, 500, 502, 503, 504}
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                response = await self.client.post(
                    self.endpoint,
                    headers=headers,
                    data=data,
                    files={
                        "file": (
                            filename,
                            audio,
                            content_type,
                        )
                    },
                )

                if response.status_code not in retryable:
                    response.raise_for_status()

                    payload = response.json()

                    value = str(
                        payload.get("transcript") or ""
                    ).strip()

                    if not value:
                        raise SpeechServiceError(
                            "Sarvam returned an empty transcript."
                        )

                    return Transcript(
                        text=value,
                        language_code=str(
                            payload.get("language_code") or language
                        ),
                    )

                last_error = SpeechServiceError(
                    f"Sarvam temporarily returned HTTP "
                    f"{response.status_code}."
                )

            except (httpx.TimeoutException, httpx.NetworkError) as error:
                last_error = error

            if attempt < 2:
                await asyncio.sleep(0.08 * (2**attempt))

        raise SpeechServiceError(
            "Speech transcription failed after three attempts."
        ) from last_error

    async def close(self) -> None:
        await self.client.aclose()