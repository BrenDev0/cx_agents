from unittest.mock import AsyncMock

import pytest

from src.embeddings.openai.service import OpenaiEmbeddingService


@pytest.fixture
def mock_openai_client(monkeypatch) -> AsyncMock:
    """Mocks openai.AsyncOpenAI so OpenaiEmbeddingService wraps a mock client
    instead of hitting the real API."""
    client = AsyncMock()
    monkeypatch.setattr(
        "src.embeddings.openai.service.AsyncOpenAI",
        lambda *args, **kwargs: client
    )
    return client


@pytest.fixture
def service(mock_openai_client: AsyncMock) -> OpenaiEmbeddingService:
    return OpenaiEmbeddingService(api_key="test-key")
