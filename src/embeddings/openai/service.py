from typing import Any
from uuid import uuid4

from openai import AsyncOpenAI

from src.vector_store.models import DocumentChunk, EmbeddingResult
from ..chunking import chunk_text

class OpenaiEmbeddingService:
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-large",
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ):
        self._model = model
        self._client = AsyncOpenAI(api_key=api_key)
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def embed_query(
        self,
        query: str
    ) -> list[float]:
        response = await self._client.embeddings.create(
            input=query,
            model=self._model
        )

        if not response.data:
            raise ValueError("No embedding data returned from provider")

        return response.data[0].embedding

    async def embed_document(
        self,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> EmbeddingResult:
        texts = chunk_text(
            content,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap
        )

        if not texts:
            return EmbeddingResult(chunks=[], embeddings=[])

        response = await self._client.embeddings.create(
            input=texts,
            model=self._model
        )

        if not response.data:
            raise ValueError("No embedding data returned from provider")

        chunks = [
            DocumentChunk(
                content=text,
                metadata=metadata or {},
                chunk_id=uuid4()
            )
            for text in texts
        ]

        embeddings = [item.embedding for item in response.data]

        return EmbeddingResult(chunks=chunks, embeddings=embeddings)
