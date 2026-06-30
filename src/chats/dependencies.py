from fastapi import Depends

from src.cache.dependencies import get_cache_store
from src.cache.types import CacheStore

from .schemas import ChatRequest
from .cache_keys import get_blocked_channel_key, get_last_message_id_key

async def is_channel_blocked(
    data: ChatRequest,
    cache_store: CacheStore = Depends(get_cache_store)
) -> bool:
    key = get_blocked_channel_key(contact_id=data.contact_id, channel=data.channel)

    return bool(await cache_store.get_bool(key))


async def _block_channel(
    cache_store: CacheStore,
    contact_id: str,
    channel: str,
) -> None:
    key = get_blocked_channel_key(contact_id=contact_id, channel=channel)

    await cache_store.store_bool(
        key,
        data=True,
        expire_seconds=3500,
    )


async def should_reply(
    data: ChatRequest,
    channel_is_blocked: bool = Depends(is_channel_blocked),
    cache_store: CacheStore = Depends(get_cache_store)
):
    if channel_is_blocked:
        return False
    
    key = get_last_message_id_key(contact_id=data.contact_id, channel=data.channel)
    last_sent_id = await cache_store.get_str(key)

    if not last_sent_id:
        return True

    outbound_messages = [
        message["id"] for message in data.chat_history if message.get("direction", "") == "outbound"
    ]

    if outbound_messages and str(last_sent_id) == str(outbound_messages[-1]):
        return True

    await _block_channel(
        cache_store=cache_store,
        channel=data.channel,
        contact_id=data.contact_id
    )

    return False

    

    