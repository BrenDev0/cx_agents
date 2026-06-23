from fastapi import Depends

from src.cache.dependencies import get_cache_store
from src.cache.protocols import CacheStore

from .schemas import ChatRequest
from .cache_keys import ChatCacheKey

async def is_channel_blocked(
    data: ChatRequest,
    cache_store: CacheStore = Depends(get_cache_store) 
) -> bool:
    channel = data.channel
    key = f"{data.contact_id}:{ChatCacheKey.BLOCKED_CHANNELS}"
        
    blocked_channels = await cache_store.get(key)

    if blocked_channels and channel in blocked_channels:
        return True
    
    return False


async def _block_channel(
    cache_store: CacheStore,
    contact_id: str,
    channel: str,
) -> None:
    key = f"{contact_id}:{ChatCacheKey.BLOCKED_CHANNELS.value}"

    blocked_channels = await cache_store.get(key) or {}

    if not isinstance(blocked_channels, dict):
        raise TypeError("Blocked channels cache value must be a dictionary.")

    blocked_channels[channel] = "blocked"

    await cache_store.store(
        key,
        data=blocked_channels,
        expire_seconds=3500,
    )


async def should_reply(
    data: ChatRequest,
    channel_is_blocked: bool = Depends(is_channel_blocked),
    cache_store: CacheStore = Depends(get_cache_store)
):
    if channel_is_blocked:
        return False
    
    key = f"{data.contact_id}:{ChatCacheKey.LAST_SENT_MESSAGE_ID}:{data.channel}"
    last_sent_id = await cache_store.get(key)

    if not last_sent_id:
        return True

    outbound_messages = [
        message.id for message in data.chat_history if message.get("direction", "") == "outbound"
    ]

    if str(last_sent_id) == str(outbound_messages[0]):
        return True
    
    
    return False

    

    