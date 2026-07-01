import json

from src.cache.redis.cache_store import RedisCacheStore
from unittest.mock import AsyncMock


async def test_store_json_serializes_and_sets_with_expiry(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.set.return_value = True

    result = await store.store_json(key="k", data={"a": 1}, expire_seconds=60)

    assert result is True
    mock_redis.set.assert_awaited_once_with(name="k", value=json.dumps({"a": 1}), ex=60)


async def test_store_json_returns_false_when_redis_returns_falsy(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.set.return_value = None

    result = await store.store_json(key="k", data={"a": 1}, expire_seconds=60)

    assert result is False


async def test_store_str_sets_raw_value(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.set.return_value = True

    result = await store.store_str(key="k", data="hello", expire_seconds=30)

    assert result is True
    mock_redis.set.assert_awaited_once_with(name="k", value="hello", ex=30)


async def test_store_int_converts_to_string(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.set.return_value = True

    result = await store.store_int(key="k", data=42, expire_seconds=30)

    assert result is True
    mock_redis.set.assert_awaited_once_with(name="k", value="42", ex=30)


async def test_store_bool_converts_to_lowercase_string(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.set.return_value = True

    result = await store.store_bool(key="k", data=True, expire_seconds=30)

    assert result is True
    mock_redis.set.assert_awaited_once_with(name="k", value="true", ex=30)


async def test_store_bool_false_converts_to_lowercase_string(store: RedisCacheStore, mock_redis: AsyncMock):
    await store.store_bool(key="k", data=False, expire_seconds=30)

    mock_redis.set.assert_awaited_once_with(name="k", value="false", ex=30)


async def test_get_json_returns_parsed_dict(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = json.dumps({"a": 1})

    result = await store.get_json("k")

    assert result == {"a": 1}
    mock_redis.get.assert_awaited_once_with(name="k")


async def test_get_json_returns_none_when_missing(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = None

    result = await store.get_json("k")

    assert result is None


async def test_get_str_returns_value(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = "hello"

    result = await store.get_str("k")

    assert result == "hello"
    mock_redis.get.assert_awaited_once_with(name="k")


async def test_get_str_returns_none_when_missing(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = None

    result = await store.get_str("k")

    assert result is None


async def test_get_int_parses_string(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = "42"

    result = await store.get_int("k")

    assert result == 42


async def test_get_int_returns_none_when_missing(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = None

    result = await store.get_int("k")

    assert result is None


async def test_get_bool_returns_true_for_true_string(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = "true"

    assert await store.get_bool("k") is True


async def test_get_bool_returns_false_for_non_true_string(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = "false"

    assert await store.get_bool("k") is False


async def test_get_bool_returns_none_when_missing(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.get.return_value = None

    assert await store.get_bool("k") is None


async def test_expire_delegates_to_redis(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.expire.return_value = True

    result = await store.expire(key="k", expire_seconds=120)

    assert result is True
    mock_redis.expire.assert_awaited_once_with(name="k", time=120)


async def test_increment_delegates_to_redis(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.incr.return_value = 5

    result = await store.increment("k")

    assert result == 5
    mock_redis.incr.assert_awaited_once_with(name="k")


async def test_remove_returns_true_when_key_deleted(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.delete.return_value = 1

    result = await store.remove("k")

    assert result is True
    mock_redis.delete.assert_awaited_once_with("k")


async def test_remove_returns_false_when_key_missing(store: RedisCacheStore, mock_redis: AsyncMock):
    mock_redis.delete.return_value = 0

    result = await store.remove("k")

    assert result is False


async def test_close_connection_closes_underlying_client(store: RedisCacheStore, mock_redis: AsyncMock):
    await store.close_connection()

    mock_redis.close.assert_awaited_once()
