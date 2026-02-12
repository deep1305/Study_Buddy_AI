from __future__ import annotations

from langchain_ollama import ChatOllama

from src.config.settings import Settings, settings


def get_ollama_llm(cfg: Settings = settings) -> ChatOllama:
    """
    Create an Ollama chat model client.

    Note: `max_retries` is not a constructor argument for ChatOllama, so retries
    (if desired) should be implemented at the call layer.
    """
    return ChatOllama(
        model=cfg.ollama_model,
        base_url=cfg.ollama_base_url,
        temperature=cfg.temperature,
    )

