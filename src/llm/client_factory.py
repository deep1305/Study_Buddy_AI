from __future__ import annotations

from typing import Union

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from src.config.settings import Settings, settings
from src.llm.groq_client import get_groq_llm
from src.llm.ollama_client import get_ollama_llm


LLMClient = Union[ChatGroq, ChatOllama]


def get_llm(cfg: Settings = settings) -> LLMClient:
    """
    Return the active LLM client based on configuration.
    """
    if cfg.use_ollama:
        return get_ollama_llm(cfg)
    return get_groq_llm(cfg)

