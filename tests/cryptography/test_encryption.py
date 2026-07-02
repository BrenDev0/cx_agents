from cryptography.fernet import Fernet, InvalidToken
import pytest

from src.cryptography.encryption import get_fernet, encrypt, decrypt


def test_get_fernet_returns_fernet_instance(encryption_key):
    assert isinstance(get_fernet(), Fernet)


def test_encrypt_returns_str_different_from_input(encryption_key):
    result = encrypt("hello world")

    assert isinstance(result, str)
    assert result != "hello world"


def test_encrypt_accepts_int(encryption_key):
    result = encrypt(42)

    assert decrypt(result) == "42"


def test_encrypt_decrypt_round_trip(encryption_key):
    encrypted = encrypt("sensitive-data")

    assert decrypt(encrypted) == "sensitive-data"


def test_encrypt_is_not_deterministic(encryption_key):
    first = encrypt("same-value")
    second = encrypt("same-value")

    assert first != second
    assert decrypt(first) == decrypt(second) == "same-value"


def test_decrypt_raises_on_tampered_token(encryption_key):
    encrypted = encrypt("sensitive-data")

    with pytest.raises(InvalidToken):
        decrypt(encrypted[:-1] + ("A" if encrypted[-1] != "A" else "B"))


def test_decrypt_raises_with_wrong_key(encryption_key, monkeypatch):
    from src.settings import settings

    encrypted = encrypt("sensitive-data")

    monkeypatch.setattr(settings, "ENCRYPTION_KEY", Fernet.generate_key().decode())

    with pytest.raises(InvalidToken):
        decrypt(encrypted)
