from src.cryptography.services import DefaultCryptographyService


def make_service(**overrides) -> DefaultCryptographyService:
    calls: dict[str, tuple] = {}

    def encrypt(data):
        calls["encrypt"] = (data,)
        return "encrypted"

    def decrypt(encrypted):
        calls["decrypt"] = (encrypted,)
        return "decrypted"

    def verify_password(unhashed_password, hashed_password):
        calls["verify_password"] = (unhashed_password, hashed_password)
        return True

    def deterministic_hash(str_to_hash):
        calls["deterministic_hash"] = (str_to_hash,)
        return "hashed-deterministic"

    def hash_token(value):
        calls["hash_token"] = (value,)
        return "hashed-token"

    def hash_password(str_to_hash):
        calls["hash_password"] = (str_to_hash,)
        return "hashed-password"

    service = DefaultCryptographyService(
        encrypt=overrides.get("encrypt", encrypt),
        decrypt=overrides.get("decrypt", decrypt),
        verify_password=overrides.get("verify_password", verify_password),
        deterministic_hash=overrides.get("deterministic_hash", deterministic_hash),
        hash_token=overrides.get("hash_token", hash_token),
        hash_password=overrides.get("hash_password", hash_password),
    )
    return service, calls


def test_encrypt_delegates_to_injected_fn():
    service, calls = make_service()

    result = service.encrypt("plain")

    assert result == "encrypted"
    assert calls["encrypt"] == ("plain",)


def test_decrypt_delegates_to_injected_fn():
    service, calls = make_service()

    result = service.decrypt("cipher")

    assert result == "decrypted"
    assert calls["decrypt"] == ("cipher",)


def test_verify_password_delegates_to_injected_fn_with_kwargs():
    service, calls = make_service()

    result = service.verify_password(unhashed_password="pw", hashed_password="hashed")

    assert result is True
    assert calls["verify_password"] == ("pw", "hashed")


def test_deterministic_hash_delegates_to_injected_fn():
    service, calls = make_service()

    result = service.deterministic_hash("value")

    assert result == "hashed-deterministic"
    assert calls["deterministic_hash"] == ("value",)


def test_hash_token_delegates_to_injected_fn():
    service, calls = make_service()

    result = service.hash_token("webhook-secret")

    assert result == "hashed-token"
    assert calls["hash_token"] == ("webhook-secret",)


def test_hash_password_delegates_to_injected_fn():
    service, calls = make_service()

    result = service.hash_password("plain-password")

    assert result == "hashed-password"
    assert calls["hash_password"] == ("plain-password",)
