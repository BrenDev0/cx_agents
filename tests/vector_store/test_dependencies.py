import pytest
from fastapi import HTTPException

from src.vector_store.dependencies import get_vector_store


class FakeState:
    def __init__(self, vector_store=None):
        if vector_store is not None:
            self.vector_store = vector_store


class FakeApp:
    def __init__(self, vector_store=None):
        self.state = FakeState(vector_store)


class FakeRequest:
    def __init__(self, vector_store=None):
        self.app = FakeApp(vector_store)


def test_get_vector_store_returns_store_when_configured():
    fake_store = object()

    result = get_vector_store(FakeRequest(vector_store=fake_store))

    assert result is fake_store


def test_get_vector_store_raises_when_not_configured():
    with pytest.raises(HTTPException) as exc_info:
        get_vector_store(FakeRequest())

    assert exc_info.value.status_code == 500


def test_get_vector_store_raises_when_state_is_none():
    with pytest.raises(HTTPException) as exc_info:
        get_vector_store(FakeRequest(vector_store=None))

    assert exc_info.value.status_code == 500
