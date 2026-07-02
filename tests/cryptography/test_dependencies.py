import pytest

from src.cryptography.dependencies import get_cryptography_service


class FakeState:
    def __init__(self, cryptography=None):
        if cryptography is not None:
            self.cryptography = cryptography


class FakeApp:
    def __init__(self, cryptography=None):
        self.state = FakeState(cryptography)


class FakeRequest:
    def __init__(self, cryptography=None):
        self.app = FakeApp(cryptography)


def test_get_cryptography_service_returns_service_when_configured(fake_cryptography_service):
    result = get_cryptography_service(FakeRequest(cryptography=fake_cryptography_service))

    assert result is fake_cryptography_service


def test_get_cryptography_service_raises_when_not_configured():
    with pytest.raises(ValueError):
        get_cryptography_service(FakeRequest())


def test_get_cryptography_service_raises_when_state_is_none():
    with pytest.raises(ValueError):
        get_cryptography_service(FakeRequest(cryptography=None))
