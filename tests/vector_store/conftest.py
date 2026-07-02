from unittest.mock import AsyncMock

import pytest

from src.vector_store.qdrant.vector_store import QdrantVectorStore


@pytest.fixture
def mock_qdrant_client(monkeypatch) -> AsyncMock:
    """Mocks qdrant_client.AsyncQdrantClient so QdrantVectorStore wraps a mock
    client instead of opening a real connection."""
    client = AsyncMock()
    monkeypatch.setattr(
        "src.vector_store.qdrant.vector_store.AsyncQdrantClient",
        lambda *args, **kwargs: client
    )
    return client


@pytest.fixture
def store(mock_qdrant_client: AsyncMock) -> QdrantVectorStore:
    return QdrantVectorStore(url="http://localhost:6333", api_key=None, collection_name="test-collection")
