from enum import StrEnum

class ChatCacheKey(StrEnum):
    WHATSAPP_BLOCK = "chats:whatsapp:blocked"
    MESSENGER_BLOCK = "chats:messenger:blocked"
    INSTAGRAM_BLOCK = "chats.ig.blocked"
    LAST_SENT_MESSAGE_ID = "chats:messages:last_id"