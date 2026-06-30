from typing import Protocol

class EmbeddingService(Protocol):
    async def embed_query(
        self,
        query: str
    ) -> list[float]: 
        ...