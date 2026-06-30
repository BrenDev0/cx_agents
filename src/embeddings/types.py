from typing import Any, Protocol

from src.vector_store.models import EmbeddingResult


class EmbeddingService(Protocol):
    async def embed_query(
        self,
        query: str
    ) -> list[float]:
        ...

    async def embed_document(
        self,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> EmbeddingResult:
        ...
