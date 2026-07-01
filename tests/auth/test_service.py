import pytest

from src.auth.cache_keys import (
    get_verification_code_key,
    get_verification_attempts_key,
    get_registration_blocked_key,
)
from src.auth.service import (
    ensure_not_blocked_from_registration,
    verify_code_or_raise,
    generate_random_code,
)
from src.exceptions import RequestBlockedException, BadRequestException
from src.settings import settings


def test_generate_random_code_default_length_is_six_digits():
    code = generate_random_code()
    assert 100000 <= code <= 999999


def test_generate_random_code_respects_custom_length():
    code = generate_random_code(length=4)
    assert 1000 <= code <= 9999


async def test_ensure_not_blocked_returns_true_when_not_blocked(fake_cache_store):
    assert await ensure_not_blocked_from_registration(email_hash="abc", cache_store=fake_cache_store) is True


async def test_ensure_not_blocked_raises_when_blocked(fake_cache_store):
    blocked_key = get_registration_blocked_key(email_hash="abc")
    await fake_cache_store.store_bool(key=blocked_key, data=True, expire_seconds=60)

    with pytest.raises(RequestBlockedException):
        await ensure_not_blocked_from_registration(email_hash="abc", cache_store=fake_cache_store)


async def test_verify_code_raises_when_no_code_cached(fake_cache_store):
    with pytest.raises(BadRequestException):
        await verify_code_or_raise(code_from_user="123456", email_hash="abc", cache_store=fake_cache_store)


async def test_verify_code_succeeds_and_clears_cache(fake_cache_store):
    email_hash = "abc"
    code_key = get_verification_code_key(email_hash)
    await fake_cache_store.store_int(key=code_key, data=123456, expire_seconds=60)

    result = await verify_code_or_raise(code_from_user="123456", email_hash=email_hash, cache_store=fake_cache_store)

    assert result is True
    assert await fake_cache_store.get_int(code_key) is None


async def test_verify_code_wrong_code_increments_attempts(fake_cache_store):
    email_hash = "abc"
    await fake_cache_store.store_int(key=get_verification_code_key(email_hash), data=123456, expire_seconds=60)

    with pytest.raises(BadRequestException):
        await verify_code_or_raise(code_from_user="000000", email_hash=email_hash, cache_store=fake_cache_store)

    assert await fake_cache_store.get_int(get_verification_attempts_key(email_hash)) == 1


async def test_verify_code_blocks_after_max_attempts(fake_cache_store):
    email_hash = "abc"
    await fake_cache_store.store_int(key=get_verification_code_key(email_hash), data=123456, expire_seconds=60)

    for _ in range(settings.REGISTRATION_MAX_ATTEMPS):
        with pytest.raises(BadRequestException):
            await verify_code_or_raise(code_from_user="000000", email_hash=email_hash, cache_store=fake_cache_store)

    assert await fake_cache_store.get_bool(get_registration_blocked_key(email_hash)) is True

    with pytest.raises(RequestBlockedException):
        await verify_code_or_raise(code_from_user="123456", email_hash=email_hash, cache_store=fake_cache_store)
