from typing import Any
from uuid import UUID

from qdrant_client import AsyncQdrantClient, models

from src.vector_store.models import DocumentChunk, EmbeddingResult


class QdrantVectorStore:
    def __init__(
        self,
        url: str,
        api_key: str | None,
        collection_name: str
    ):
        self._collection_name = collection_name
        self._client = AsyncQdrantClient(url=url, api_key=api_key)

    async def upsert(self, result: EmbeddingResult) -> None:
        points = [
            models.PointStruct(
                id=str(chunk.chunk_id),
                vector=embedding,
                payload={"content": chunk.content, "metadata": chunk.metadata}
            )
            for chunk, embedding in zip(result.chunks, result.embeddings)
        ]

        await self._client.upsert(collection_name=self._collection_name, points=points)

    async def query(
        self,
        embedding: list[float],
        top_k: int = 5,
        filter: dict[str, Any] | None = None
    ) -> list[DocumentChunk]:
        results = await self._client.query_points(
            collection_name=self._collection_name,
            query=embedding,
            limit=top_k,
            query_filter=self._build_filter(filter)
        )

        return [
            DocumentChunk(
                content=point.payload["content"],
                metadata=point.payload.get("metadata", {}),
                chunk_id=UUID(str(point.id))
            )
            for point in results.points
        ]

    async def delete(self, chunk_ids: list[UUID]) -> bool:
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=models.PointIdsList(points=[str(chunk_id) for chunk_id in chunk_ids])
        )

        return True

    async def delete_by_filter(self, filter: dict[str, Any]) -> bool:
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=models.FilterSelector(filter=self._build_filter(filter))
        )

        return True

    def _build_filter(self, filter: dict[str, Any] | None) -> models.Filter | None:
        if not filter:
            return None

        return models.Filter(
            must=[
                models.FieldCondition(key=f"metadata.{key}", match=models.MatchValue(value=value))
                for key, value in filter.items()
            ]
        )

    async def close(self) -> None:
        await self._client.close()
