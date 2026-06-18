from fastapi import Depends, HTTPException

from src.cache.dependencies import get_cache_store
from src.cache.protocols import CacheStore

from .schemas import ChatRequest
from .cache_keys import ChatCacheKey

async def is_channel_blocked(
    data: ChatRequest,
    cache_store: CacheStore = Depends(get_cache_store) 
) -> bool:
    channel = data.channel
    key = ChatCacheKey.BLOCKED_CHANNELS
        
    blocked_channels = cache_store.get(key)

    if blocked_channels and channel in blocked_channels:
        return True
    
    return False


async def should_reply(
    data: ChatRequest,
    channel_is_blocked: bool = Depends(is_channel_blocked),
    cache_store: CacheStore = Depends(get_cache_store)
):
    if channel_is_blocked:
        return False
    
    key = ChatCacheKey.LAST_SENT_MESSAGE_ID

    last_message_id_in_history = data.chat_history[0].id

    