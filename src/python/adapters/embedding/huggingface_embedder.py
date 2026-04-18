from __future__ import annotations

import logging

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

logger = logging.getLogger(__name__)


class HuggingFaceEmbedder:
    """Embedding adapter using HuggingFace sentence-transformers via LlamaIndex."""

    def __init__(self, model_name: str = "sdadas/mmlw-roberta-large") -> None:
        logger.info("Loading embedding model: %s", model_name)
        self._embed_model = HuggingFaceEmbedding(model_name=model_name)
        self._dimension = self._detect_dimension()

    def _detect_dimension(self) -> int:
        test_vec = self._embed_model.get_text_embedding("test")
        return len(test_vec)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [self._embed_model.get_text_embedding(t) for t in texts]

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def llama_index_model(self) -> HuggingFaceEmbedding:
        """Access the underlying LlamaIndex embedding model for pipeline integration."""
        return self._embed_model
