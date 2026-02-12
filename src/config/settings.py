from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _to_bool(v: str) -> bool:
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _to_float(v: str, default: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _to_int(v: str, default: int) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    # Provider toggle
    use_ollama: bool

    # Groq
    groq_api_key: str | None
    groq_model: str

    # Ollama
    ollama_model: str
    ollama_base_url: str

    # Generation params
    temperature: float
    max_retries: int

    @property
    def rag_model(self) -> str:
        return self.ollama_model if self.use_ollama else self.groq_model


def get_settings() -> Settings:
    """
    Loads environment variables (from .env if present) and returns validated settings.

    Env vars supported:
    - USE_OLLAMA (true/false)
    - GROQ_API_KEY
    - GROQ_MODEL
    - OLLAMA_MODEL
    - OLLAMA_BASE_URL
    - TEMPERATURE
    - MAX_RETRIES
    """
    load_dotenv()

    s = Settings(
        use_ollama=_to_bool(os.getenv("USE_OLLAMA", "false")),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        ollama_model=os.getenv("OLLAMA_MODEL", "glm-4.7-flash:q4_K_M").strip(),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=_to_float(os.getenv("TEMPERATURE", "0.9"), 0.9),
        max_retries=_to_int(os.getenv("MAX_RETRIES", "3"), 3),
    )

    if not s.use_ollama and not s.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is required when USE_OLLAMA=false")

    # Typical model temperature range is 0..2 (many providers use 0..1).
    if not (0.0 <= s.temperature <= 2.0):
        raise RuntimeError("TEMPERATURE must be between 0.0 and 2.0")

    if s.max_retries < 0:
        raise RuntimeError("MAX_RETRIES must be >= 0")

    return s


# Backwards-compatible convenience for existing imports:
settings = get_settings()