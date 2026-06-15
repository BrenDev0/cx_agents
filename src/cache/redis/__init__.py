from redis import asyncio as redis

from typing import Any

class RedisCacheStore:
    def __init__(self, connection_url: str):
        self.redis = redis.from_url(connection_url)

    async def store(
        self,
        key: str,
        data: dict[str, Any]
    ):
        pass