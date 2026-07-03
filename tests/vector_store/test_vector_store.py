from unittest.mock import AsyncMock
from uuid import uuid4

from qdrant_client import models

from src.vector_store.models import DocumentChunk, EmbeddingResult
from src.vector_store.qdrant.vector_store import QdrantVectorStore


class FakePoint:
    def __init__(self, id, payload):
        self.id = id
        self.payload = payload


class FakeQueryResponse:
    def __init__(self, points):
        self.points = points


def make_chunk(**overrides) -> DocumentChunk:
    defaults = dict(content="hello world", metadata={"source": "test"}, chunk_id=uuid4())
    defaults.update(overrides)
    return DocumentChunk(**defaults)


async def test_ensure_collection_skips_create_when_collection_already_exists(
    store: QdrantVectorStore, mock_qdrant_client: AsyncMock
):
    mock_qdrant_client.collection_exists.return_value = True

    await store.ensure_collection(vector_size=3072)

    mock_qdrant_client.collection_exists.assert_awaited_once_with("test-collection")
    mock_qdrant_client.create_collection.assert_not_awaited()


async def test_ensure_collection_creates_it_when_missing(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    mock_qdrant_client.collection_exists.return_value = False

    await store.ensure_collection(vector_size=3072)

    mock_qdrant_client.create_collection.assert_awaited_once_with(
        collection_name="test-collection",
        vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE)
    )


async def test_ensure_collection_uses_given_distance(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    mock_qdrant_client.collection_exists.return_value = False

    await store.ensure_collection(vector_size=1536, distance=models.Distance.DOT)

    mock_qdrant_client.create_collection.assert_awaited_once_with(
        collection_name="test-collection",
        vectors_config=models.VectorParams(size=1536, distance=models.Distance.DOT)
    )


async def test_upsert_sends_points_built_from_chunks_and_embeddings(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    chunk_1 = make_chunk(content="first", metadata={"a": 1})
    chunk_2 = make_chunk(content="second", metadata={"b": 2})
    result = EmbeddingResult(chunks=[chunk_1, chunk_2], embeddings=[[0.1, 0.2], [0.3, 0.4]])

    await store.upsert(result)

    mock_qdrant_client.upsert.assert_awaited_once_with(
        collection_name="test-collection",
        points=[
            models.PointStruct(
                id=str(chunk_1.chunk_id), vector=[0.1, 0.2], payload={"content": "first", "metadata": {"a": 1}}
            ),
            models.PointStruct(
                id=str(chunk_2.chunk_id), vector=[0.3, 0.4], payload={"content": "second", "metadata": {"b": 2}}
            ),
        ]
    )


async def test_upsert_with_no_chunks_sends_empty_points(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    result = EmbeddingResult(chunks=[], embeddings=[])

    await store.upsert(result)

    mock_qdrant_client.upsert.assert_awaited_once_with(collection_name="test-collection", points=[])


async def test_query_returns_document_chunks_from_points(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    chunk_id = uuid4()
    mock_qdrant_client.query_points.return_value = FakeQueryResponse(
        points=[FakePoint(id=str(chunk_id), payload={"content": "hello world", "metadata": {"source": "test"}})]
    )

    results = await store.query(embedding=[0.1, 0.2], top_k=3)

    assert results == [DocumentChunk(content="hello world", metadata={"source": "test"}, chunk_id=chunk_id)]
    mock_qdrant_client.query_points.assert_awaited_once_with(
        collection_name="test-collection", query=[0.1, 0.2], limit=3, query_filter=None
    )


async def test_query_defaults_missing_metadata_to_empty_dict(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    chunk_id = uuid4()
    mock_qdrant_client.query_points.return_value = FakeQueryResponse(
        points=[FakePoint(id=str(chunk_id), payload={"content": "hello world"})]
    )

    results = await store.query(embedding=[0.1, 0.2])

    assert results[0].metadata == {}


async def test_query_returns_empty_list_when_no_points_found(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    mock_qdrant_client.query_points.return_value = FakeQueryResponse(points=[])

    results = await store.query(embedding=[0.1, 0.2])

    assert results == []


async def test_query_builds_filter_from_metadata_dict(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    mock_qdrant_client.query_points.return_value = FakeQueryResponse(points=[])

    await store.query(embedding=[0.1, 0.2], filter={"user_id": "123"})

    expected_filter = models.Filter(
        must=[models.FieldCondition(key="metadata.user_id", match=models.MatchValue(value="123"))]
    )
    mock_qdrant_client.query_points.assert_awaited_once_with(
        collection_name="test-collection", query=[0.1, 0.2], limit=5, query_filter=expected_filter
    )


async def test_delete_calls_client_with_point_ids(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    chunk_id_1 = uuid4()
    chunk_id_2 = uuid4()

    result = await store.delete([chunk_id_1, chunk_id_2])

    assert result is True
    mock_qdrant_client.delete.assert_awaited_once_with(
        collection_name="test-collection",
        points_selector=models.PointIdsList(points=[str(chunk_id_1), str(chunk_id_2)])
    )


async def test_delete_by_filter_deletes_and_returns_true_when_filter_given(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    result = await store.delete_by_filter({"user_id": "123"})

    assert result is True
    expected_filter = models.Filter(
        must=[models.FieldCondition(key="metadata.user_id", match=models.MatchValue(value="123"))]
    )
    mock_qdrant_client.delete.assert_awaited_once_with(
        collection_name="test-collection",
        points_selector=models.FilterSelector(filter=expected_filter)
    )


async def test_delete_by_filter_returns_false_and_skips_client_when_filter_empty(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    result = await store.delete_by_filter({})

    assert result is False
    mock_qdrant_client.delete.assert_not_awaited()


async def test_close_closes_underlying_client(store: QdrantVectorStore, mock_qdrant_client: AsyncMock):
    await store.close()

    mock_qdrant_client.close.assert_awaited_once()
