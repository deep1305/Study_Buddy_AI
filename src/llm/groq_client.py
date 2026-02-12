from __future__ import annotations

from langchain_groq import ChatGroq

from src.config.settings import Settings, settings


def get_groq_llm(cfg: Settings = settings) -> ChatGroq:
    """
    Create a Groq chat model client.

    Uses values from `src.config.settings.settings` by default.
    """
    return ChatGroq(
        api_key=cfg.groq_api_key,
        model=cfg.groq_model,
        temperature=cfg.temperature,
        max_retries=cfg.max_retries,
    )