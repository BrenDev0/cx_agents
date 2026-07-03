from src.cryptography.hashing import deterministic_hash, hash_token, hash_password, verify_password


def test_deterministic_hash_is_stable():
    assert deterministic_hash("user@example.com") == deterministic_hash("user@example.com")


def test_deterministic_hash_is_case_insensitive():
    assert deterministic_hash("User@Example.com") == deterministic_hash("user@example.com")


def test_deterministic_hash_differs_for_different_input():
    assert deterministic_hash("a@example.com") != deterministic_hash("b@example.com")


def test_deterministic_hash_matches_sha256():
    import hashlib

    expected = hashlib.sha256("user@example.com".encode("utf-8")).hexdigest()

    assert deterministic_hash("user@example.com") == expected


def test_hash_token_is_stable():
    assert hash_token("aB3-secret") == hash_token("aB3-secret")


def test_hash_token_is_case_sensitive():
    assert hash_token("AB3-secret") != hash_token("ab3-secret")


def test_hash_token_differs_for_different_input():
    assert hash_token("token-a") != hash_token("token-b")


def test_hash_password_returns_different_value_than_input():
    hashed = hash_password("s3cret-password")

    assert hashed != "s3cret-password"


def test_hash_password_is_not_deterministic():
    first = hash_password("s3cret-password")
    second = hash_password("s3cret-password")

    assert first != second


def test_verify_password_succeeds_for_correct_password():
    hashed = hash_password("s3cret-password")

    assert verify_password("s3cret-password", hashed) is True


def test_verify_password_fails_for_incorrect_password():
    hashed = hash_password("s3cret-password")

    assert verify_password("wrong-password", hashed) is False
