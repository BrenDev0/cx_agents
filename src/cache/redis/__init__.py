import redis.asyncio as redis

import json
from typing import Any


class RedisCacheStore:
    def __init__(self, connection_url: str):
        self._redis = redis.from_url(connection_url)

    async def store(
        self,
        key: str,
        data: dict[str, Any],
        expire_seconds: int
    )-> bool:
        result = await self._redis.set(
            name=key,
            value=json.dumps(data),
            ex=expire_seconds
        )

        return bool(result)
    
    async def get(self, key: str) -> Any | None:
        data = await self._redis.get(name=key)
        if data is None:
            return None
        
        return json.loads(data)
    
    async def expire(
        self, 
        key:str, 
        expire_seconds: int
    )-> bool: 
        return await self._redis.expire(
            name=key,
            time=expire_seconds
        )
    
    async def increment(self, key: str) -> int:
        return await self._redis.incr(name=key)
    
    async def remove(self, key: str) -> bool:
        result = await self._redis.delete(key)
        return bool(result)
    
    async def close_connection(self):
        await self._redis.close()