from fastapi import Depends
from src.cache.dependencies import get_cache_store
from src.cache.types import CacheStore

from src.types import ChatMessage, MessageRole


from .cache_keys import  get_blocked_channel_key, get_last_message_id_key


async def is_channel_blocked(
    contact_id: str,
    channel: str,
    cache_store: CacheStore = Depends(get_cache_store)
) -> bool:
    key = get_blocked_channel_key(contact_id=contact_id, channel=channel)

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
    contact_id: str,
    channel: str,
    chat_history: list[ChatMessage],
    channel_is_blocked: bool = Depends(is_channel_blocked),
    cache_store: CacheStore = Depends(get_cache_store)
):
    if channel_is_blocked:
        return False

    key = get_last_message_id_key(contact_id, channel=channel)
    last_sent_id = await cache_store.get_str(key)

    if not last_sent_id:
        return True

    outbound_messages = [
        message["id"] for message in chat_history if message.get("role", "") == MessageRole.AI
    ]

    if outbound_messages and str(last_sent_id) == str(outbound_messages[-1]):
        return True

    await _block_channel(
        cache_store=cache_store,
        channel=channel,
        contact_id=contact_id
    )

    return False

    

    