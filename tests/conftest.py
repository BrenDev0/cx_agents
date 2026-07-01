import os

# Settings() is instantiated at import time in src/settings.py, and several
# slices import it transitively (e.g. auth.service). These must be set before
# any `src.*` import happens, so this has to live at module level, not in a
# fixture.
os.environ.setdefault("RABBITMQ_USER", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")
os.environ.setdefault("RABBITMQ_PORT", "5672")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_REGION_NAME", "us-east-1")
os.environ.setdefault("AWS_BUCKET_NAME", "test-bucket")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_COLLECTION_NAME", "test-collection")

import json
from typing import Any

import pytest


class FakeCacheStore:
    """Mirrors RedisCacheStore's actual wire format (json.dumps/str conversion,
    no custom encoder) so tests catch serialization bugs a naive dict-passthrough
    fake would hide."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    async def store_json(self, key: str, data: dict[str, Any], expire_seconds: int) -> bool:
        self._data[key] = json.dumps(data)
        return True

    async def store_str(self, key: str, data: str, expire_seconds: int) -> bool:
        self._data[key] = data
        return True

    async def store_int(self, key: str, data: int, expire_seconds: int) -> bool:
        self._data[key] = str(data)
        return True

    async def store_bool(self, key: str, data: bool, expire_seconds: int) -> bool:
        self._data[key] = str(data).lower()
        return True

    async def get_json(self, key: str) -> dict[str, Any] | None:
        data = self._data.get(key)
        return json.loads(data) if data is not None else None

    async def get_str(self, key: str) -> str | None:
        return self._data.get(key)

    async def get_int(self, key: str) -> int | None:
        data = self._data.get(key)
        return int(data) if data is not None else None

    async def get_bool(self, key: str) -> bool | None:
        data = self._data.get(key)
        if data is None:
            return None
        return data == "true"

    async def expire(self, key: str, expire_seconds: int) -> bool:
        return key in self._data

    async def increment(self, key: str) -> int:
        current = int(self._data.get(key, 0)) + 1
        self._data[key] = str(current)
        return current

    async def remove(self, key: str) -> bool:
        existed = key in self._data
        self._data.pop(key, None)
        return existed


@pytest.fixture
def fake_cache_store() -> FakeCacheStore:
    return FakeCacheStore()


class FakeCryptographyService:
    """No-op but reversible transforms, so tests can assert on round-trips
    without pulling in real bcrypt/Fernet."""

    def encrypt(self, data: str | int) -> str:
        return f"enc:{data}"

    def decrypt(self, encrypted: str) -> str:
        return encrypted.removeprefix("enc:")

    def deterministic_hash(self, value: str) -> str:
        return f"hash:{value}"

    def hash_password(self, str_to_hash: str) -> str:
        return f"hashed:{str_to_hash}"

    def verify_password(self, unhashed_password: str, hashed_password: str) -> bool:
        return self.hash_password(unhashed_password) == hashed_password


@pytest.fixture
def fake_cryptography_service() -> FakeCryptographyService:
    return FakeCryptographyService()
