from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "VaaniRAG"
    environment: Literal["development", "production", "test"] = "development"
    api_bearer_token: SecretStr | None = None

    sarvam_api_key: SecretStr | None = None
    sarvam_stt_model: str = "saaras:v4"
    sarvam_chat_model: str = "sarvam-105b"
    sarvam_timeout_seconds: float = 12.0

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None
    qdrant_collection: str = "msmarco_xi_multiview_v1"
    qdrant_timeout_seconds: float = 10.0
    prefer_grpc: bool = False

    dense_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    sparse_model: str = "Qdrant/bm25"
    prefetch_limit: int = 18
    answer_limit: int = 5
    min_grounding_confidence: float = 0.30
    query_deadline_ms: float = 200.0
    enable_generative_mode: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
