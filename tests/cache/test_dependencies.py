import pytest
from fastapi import HTTPException

from src.cache.dependencies import get_cache_store


class FakeState:
    def __init__(self, cache_store=None):
        if cache_store is not None:
            self.cache_store = cache_store


class FakeApp:
    def __init__(self, cache_store=None):
        self.state = FakeState(cache_store)


class FakeRequest:
    def __init__(self, cache_store=None):
        self.app = FakeApp(cache_store)


def test_get_cache_store_returns_store_when_configured(fake_cache_store):
    result = get_cache_store(FakeRequest(cache_store=fake_cache_store))

    assert result is fake_cache_store


def test_get_cache_store_raises_when_not_configured():
    with pytest.raises(HTTPException) as exc_info:
        get_cache_store(FakeRequest())

    assert exc_info.value.status_code == 500


def test_get_cache_store_raises_when_state_is_none():
    with pytest.raises(HTTPException) as exc_info:
        get_cache_store(FakeRequest(cache_store=None))

    assert exc_info.value.status_code == 500
