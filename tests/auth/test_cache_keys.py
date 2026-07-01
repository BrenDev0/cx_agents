from uuid import uuid4

from src.auth.cache_keys import (
    get_verification_code_key,
    get_verification_attempts_key,
    get_registration_blocked_key,
    get_login_attemps_key,
    get_login_blocked_key,
    get_session_key,
    get_current_user_key,
)


def test_get_verification_code_key():
    assert get_verification_code_key("abc") == "abc:auth:registration:verification_code"


def test_get_verification_attempts_key():
    assert get_verification_attempts_key("abc") == "abc:auth:registration:attempts"


def test_get_registration_blocked_key():
    assert get_registration_blocked_key("abc") == "abc:auth:registration:blocked"


def test_get_login_attemps_key():
    assert get_login_attemps_key("user@example.com") == "user@example.com:auth:login:attempts"


def test_get_login_blocked_key():
    assert get_login_blocked_key("user@example.com") == "user@example.com:auth:login:blocked"


def test_get_session_key():
    session_id = uuid4()
    assert get_session_key(session_id) == f"auth:session:{session_id}"


def test_get_current_user_key():
    user_id = uuid4()
    assert get_current_user_key(user_id) == f"{user_id}:auth:current_user"
