from enum import StrEnum

class ChatCacheKey(StrEnum):
    BLOCKED_CHANNELS = "chats.channels.blocked"
    LAST_SENT_MESSAGE_ID = "chats:messages:last_id"


def get_blocked_channel_key(
    contact_id: str,
    channel: str
) -> str:
    return f"{contact_id}:{ChatCacheKey.BLOCKED_CHANNELS}:{channel}"


def get_last_message_id_key(
    contact_id: str,
    channel: str
) -> str:
    return f"{contact_id}:{ChatCacheKey.LAST_SENT_MESSAGE_ID}:{channel}"
