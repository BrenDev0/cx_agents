from uuid import uuid4

import pytest

from src.auth.cache_keys import get_current_user_key, get_session_key
from src.auth.dependencies import get_current_user, get_session_id
from src.exceptions import UnauthorizedException
from src.users.mappers import domain_to_cache_dict


class FakeRequest:
    def __init__(self, cookies: dict[str, str] | None = None):
        self.cookies = cookies or {}


async def test_get_session_id_raises_without_cookie():
    with pytest.raises(UnauthorizedException):
        await get_session_id(FakeRequest())


async def test_get_session_id_raises_on_invalid_uuid():
    with pytest.raises(UnauthorizedException):
        await get_session_id(FakeRequest(cookies={"session_id": "not-a-uuid"}))


async def test_get_session_id_returns_uuid_from_cookie():
    session_id = uuid4()

    result = await get_session_id(FakeRequest(cookies={"session_id": str(session_id)}))

    assert result == session_id


async def test_get_current_user_raises_when_no_session_cached(fake_cache_store):
    async def unexpected_get_user_by_id(user_id):
        raise AssertionError("should not reach the repo without a session")

    with pytest.raises(UnauthorizedException):
        await get_current_user(
            get_user_by_id=unexpected_get_user_by_id,
            cache_store=fake_cache_store,
            session_id=uuid4()
        )


async def test_get_current_user_raises_when_session_has_no_user_id(fake_cache_store):
    session_id = uuid4()
    await fake_cache_store.store_json(key=get_session_key(session_id), data={}, expire_seconds=60)

    async def unexpected_get_user_by_id(user_id):
        raise AssertionError("should not reach the repo without a user_id")

    with pytest.raises(UnauthorizedException):
        await get_current_user(
            get_user_by_id=unexpected_get_user_by_id,
            cache_store=fake_cache_store,
            session_id=session_id
        )


async def test_get_current_user_returns_cached_user_without_hitting_repo(fake_cache_store, sample_user):
    session_id = uuid4()
    await fake_cache_store.store_json(
        key=get_session_key(session_id),
        data={"user_id": str(sample_user.id)},
        expire_seconds=60
    )
    await fake_cache_store.store_json(
        key=get_current_user_key(sample_user.id),
        data=domain_to_cache_dict(sample_user),
        expire_seconds=60
    )

    async def unexpected_get_user_by_id(user_id):
        raise AssertionError("should use the cache, not the repo")

    result = await get_current_user(
        get_user_by_id=unexpected_get_user_by_id,
        cache_store=fake_cache_store,
        session_id=session_id
    )

    assert result == sample_user


async def test_get_current_user_raises_when_repo_finds_no_user(fake_cache_store):
    session_id = uuid4()
    user_id = uuid4()
    await fake_cache_store.store_json(
        key=get_session_key(session_id),
        data={"user_id": str(user_id)},
        expire_seconds=60
    )

    async def get_user_by_id_returns_none(user_id):
        return None

    with pytest.raises(UnauthorizedException):
        await get_current_user(
            get_user_by_id=get_user_by_id_returns_none,
            cache_store=fake_cache_store,
            session_id=session_id
        )


async def test_get_current_user_caches_fetched_user_on_cache_miss(fake_cache_store, sample_user):
    session_id = uuid4()
    await fake_cache_store.store_json(
        key=get_session_key(session_id),
        data={"user_id": str(sample_user.id)},
        expire_seconds=60
    )

    async def get_user_by_id_returns_sample(user_id):
        return sample_user

    result = await get_current_user(
        get_user_by_id=get_user_by_id_returns_sample,
        cache_store=fake_cache_store,
        session_id=session_id
    )

    assert result == sample_user

    cached = await fake_cache_store.get_json(get_current_user_key(sample_user.id))
    assert cached == domain_to_cache_dict(sample_user)
