from __future__ import annotations

import logging

from llama_index.llms.ollama import Ollama

logger = logging.getLogger(__name__)


class OllamaLLM:
    """LLM adapter for Ollama (on-premise inference)."""

    def __init__(
        self,
        model: str = "mistral",
        base_url: str = "http://localhost:11434",
        request_timeout: float = 120.0,
        temperature: float = 0.1,
    ) -> None:
        self._llm = Ollama(
            model=model,
            base_url=base_url,
            request_timeout=request_timeout,
            temperature=temperature,
        )
        self._model = model
        logger.info("Initialized Ollama LLM: model=%s, url=%s", model, base_url)

    def complete(self, prompt: str) -> str:
        response = self._llm.complete(prompt)
        return str(response)

    @property
    def llama_index_llm(self) -> Ollama:
        """Access the underlying LlamaIndex LLM for pipeline integration."""
        return self._llm

    @property
    def model_name(self) -> str:
        return self._model
