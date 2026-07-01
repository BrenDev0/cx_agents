from unittest.mock import AsyncMock

import pytest

from src.cache.redis.cache_store import RedisCacheStore


@pytest.fixture
def mock_redis(monkeypatch) -> AsyncMock:
    """Mocks redis.asyncio.from_url so RedisCacheStore wraps a mock client
    instead of opening a real connection."""
    client = AsyncMock()
    monkeypatch.setattr(
        "src.cache.redis.cache_store.redis.from_url",
        lambda *args, **kwargs: client
    )
    return client


@pytest.fixture
def store(mock_redis: AsyncMock) -> RedisCacheStore:
    return RedisCacheStore("redis://localhost:6379/0")
