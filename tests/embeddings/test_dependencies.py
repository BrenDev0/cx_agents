import pytest
from fastapi import HTTPException

from src.embeddings.dependencies import get_embedding_service


class FakeState:
    def __init__(self, embedding_service=None):
        if embedding_service is not None:
            self.embedding_service = embedding_service


class FakeApp:
    def __init__(self, embedding_service=None):
        self.state = FakeState(embedding_service)


class FakeRequest:
    def __init__(self, embedding_service=None):
        self.app = FakeApp(embedding_service)


def test_get_embedding_service_returns_service_when_configured():
    fake_service = object()

    result = get_embedding_service(FakeRequest(embedding_service=fake_service))

    assert result is fake_service


def test_get_embedding_service_raises_when_not_configured():
    with pytest.raises(HTTPException) as exc_info:
        get_embedding_service(FakeRequest())

    assert exc_info.value.status_code == 500


def test_get_embedding_service_raises_when_state_is_none():
    with pytest.raises(HTTPException) as exc_info:
        get_embedding_service(FakeRequest(embedding_service=None))

    assert exc_info.value.status_code == 500
