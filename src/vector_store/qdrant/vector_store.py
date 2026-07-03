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

    async def ensure_collection(
        self,
        vector_size: int,
        distance: models.Distance = models.Distance.COSINE
    ) -> None:
        if await self._client.collection_exists(self._collection_name):
            return

        await self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=distance)
        )

        # Deletes are filtered on these fields (e.g. by document_id on document
        # removal); index them so delete_by_filter doesn't degrade into a full
        # collection scan as the knowledge base grows.
        for field in ("metadata.document_id", "metadata.assistant_id", "metadata.user_id"):
            await self._client.create_payload_index(
                collection_name=self._collection_name,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD
            )

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

        chunks = []

        for point in results.points:
            payload = point.payload or {}
            chunks.append(DocumentChunk(
                content=payload["content"],
                metadata=payload.get("metadata", {}),
                chunk_id=UUID(str(point.id))
            ))

        return chunks

    async def delete(self, chunk_ids: list[UUID]) -> bool:
        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=models.PointIdsList(points=[str(chunk_id) for chunk_id in chunk_ids])
        )

        return True

    async def delete_by_filter(self, filter: dict[str, Any]) -> bool:
        built_filter = self._build_filter(filter)

        if built_filter is None:
            return False

        await self._client.delete(
            collection_name=self._collection_name,
            points_selector=models.FilterSelector(filter=built_filter)
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
