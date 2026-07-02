import string
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from src.embeddings.openai.service import OpenaiEmbeddingService
from src.vector_store.models import EmbeddingResult


class FakeEmbeddingItem:
    def __init__(self, embedding: list[float]):
        self.embedding = embedding


class FakeEmbeddingResponse:
    def __init__(self, data: list[FakeEmbeddingItem]):
        self.data = data


async def test_embed_query_returns_embedding_vector(service, mock_openai_client: AsyncMock):
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(
        data=[FakeEmbeddingItem([0.1, 0.2, 0.3])]
    )

    result = await service.embed_query("hello world")

    assert result == [0.1, 0.2, 0.3]
    mock_openai_client.embeddings.create.assert_awaited_once_with(
        input="hello world", model="text-embedding-3-large"
    )


async def test_embed_query_raises_when_no_data_returned(service, mock_openai_client: AsyncMock):
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(data=[])

    with pytest.raises(ValueError):
        await service.embed_query("hello world")


async def test_embed_document_returns_empty_result_for_empty_content(service, mock_openai_client: AsyncMock):
    result = await service.embed_document("   ")

    assert result == EmbeddingResult(chunks=[], embeddings=[])
    mock_openai_client.embeddings.create.assert_not_awaited()


async def test_embed_document_chunks_and_embeds_content(mock_openai_client: AsyncMock):
    service = OpenaiEmbeddingService(api_key="test-key", chunk_size=10, chunk_overlap=3)
    text = string.ascii_lowercase[:25]
    expected_chunks = ["abcdefghij", "hijklmnopq", "opqrstuvwx", "vwxy"]
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(
        data=[FakeEmbeddingItem([float(i)]) for i in range(len(expected_chunks))]
    )

    result = await service.embed_document(text, metadata={"source": "test"})

    assert [chunk.content for chunk in result.chunks] == expected_chunks
    assert all(chunk.metadata == {"source": "test"} for chunk in result.chunks)
    assert all(isinstance(chunk.chunk_id, UUID) for chunk in result.chunks)
    assert len({chunk.chunk_id for chunk in result.chunks}) == len(expected_chunks)
    assert result.embeddings == [[0.0], [1.0], [2.0], [3.0]]
    mock_openai_client.embeddings.create.assert_awaited_once_with(
        input=expected_chunks, model="text-embedding-3-large"
    )


async def test_embed_document_defaults_metadata_to_empty_dict(service, mock_openai_client: AsyncMock):
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(
        data=[FakeEmbeddingItem([0.1])]
    )

    result = await service.embed_document("hello world")

    assert result.chunks[0].metadata == {}


async def test_embed_document_raises_when_no_data_returned(service, mock_openai_client: AsyncMock):
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(data=[])

    with pytest.raises(ValueError):
        await service.embed_document("hello world")


async def test_embed_chunks_returns_empty_result_for_empty_list(service, mock_openai_client: AsyncMock):
    result = await service.embed_chunks([])

    assert result == EmbeddingResult(chunks=[], embeddings=[])
    mock_openai_client.embeddings.create.assert_not_awaited()


async def test_embed_chunks_embeds_pre_chunked_text_without_rechunking(service, mock_openai_client: AsyncMock):
    texts = ["first chunk", "second chunk"]
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(
        data=[FakeEmbeddingItem([0.1]), FakeEmbeddingItem([0.2])]
    )

    result = await service.embed_chunks(texts, metadata={"document_id": "abc"})

    assert [chunk.content for chunk in result.chunks] == texts
    assert all(chunk.metadata == {"document_id": "abc"} for chunk in result.chunks)
    assert result.embeddings == [[0.1], [0.2]]
    mock_openai_client.embeddings.create.assert_awaited_once_with(
        input=texts, model="text-embedding-3-large"
    )


async def test_embed_chunks_defaults_metadata_to_empty_dict(service, mock_openai_client: AsyncMock):
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(
        data=[FakeEmbeddingItem([0.1])]
    )

    result = await service.embed_chunks(["a chunk"])

    assert result.chunks[0].metadata == {}


async def test_embed_chunks_raises_when_no_data_returned(service, mock_openai_client: AsyncMock):
    mock_openai_client.embeddings.create.return_value = FakeEmbeddingResponse(data=[])

    with pytest.raises(ValueError):
        await service.embed_chunks(["a chunk"])
