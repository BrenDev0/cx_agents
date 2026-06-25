from enum import StrEnum
from typing_extensions import TypedDict


class MessageRole(StrEnum):
    SYSTEM = "system"
    HUMAN = "user"
    AI = "assistant"

class ChatMessage(TypedDict):
    role: MessageRole
    content: str
