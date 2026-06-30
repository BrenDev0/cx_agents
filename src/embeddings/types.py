from typing import Protocol

from .models import DocumentChunk

class EmbeddingService(Protocol):
    async def embed_query(
        self,
        query: str
    ) -> list[float]: 
        ...