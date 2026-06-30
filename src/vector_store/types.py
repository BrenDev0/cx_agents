from typing import Any, Protocol
from uuid import UUID

from src.embeddings.models import DocumentChunk, EmbeddingResult


class VectorStore(Protocol):
    async def upsert(self, result: EmbeddingResult) -> None: ...

    async def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        filter: dict[str, Any] | None = None
    ) -> list[DocumentChunk]: ...

    async def delete(self, chunk_ids: list[UUID]) -> bool: ...

    async def delete_by_filter(self, filter: dict[str, Any]) -> bool: ...
