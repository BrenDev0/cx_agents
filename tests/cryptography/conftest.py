import pytest
from cryptography.fernet import Fernet

from src.settings import settings


@pytest.fixture
def encryption_key(monkeypatch) -> str:
    """encryption.py reads settings.ENCRYPTION_KEY on every call, so tests
    need a real Fernet key rather than the placeholder set in tests/conftest.py."""
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(settings, "ENCRYPTION_KEY", key)
    return key
