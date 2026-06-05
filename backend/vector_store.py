"""Project-specific Chroma vector store with OpenAI and local fallback embeddings."""

from __future__ import annotations

import hashlib
import logging
import math
import os
from functools import lru_cache

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from backend.settings import settings


class HashEmbeddings(Embeddings):
    """Deterministic fallback embeddings for local tests and demos without API keys."""

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    if settings.openai_api_key:
        return OpenAIEmbeddings(model=settings.embedding_model, openai_api_key=settings.openai_api_key)
    return HashEmbeddings()


@lru_cache(maxsize=1)
def get_project_vector_store() -> Chroma:
    return Chroma(
        collection_name=settings.project_collection_name,
        persist_directory=settings.project_chroma_path,
        embedding_function=get_embeddings(),
        client_settings=ChromaSettings(anonymized_telemetry=False),
    )
