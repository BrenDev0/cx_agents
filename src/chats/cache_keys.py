from enum import StrEnum

class ChatCacheKey(StrEnum):
    BLOCKED_CHANNELS = "chats.channels.blocked"
    LAST_SENT_MESSAGE_ID = "chats:messages:last_id"