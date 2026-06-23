from uuid import UUID
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class DocumentChunk:
    content: str
    metadata: dict[str, Any]
    chunk_id: UUID


@dataclass(frozen=True)
class EmbeddingResult:
    chunks: list[DocumentChunk]
    embeddings: list[list[float]]