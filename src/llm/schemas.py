from typing import TypedDict
from uuid import UUID
from enum import StrEnum


class ChatRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(TypedDict):
    role: ChatRole
    content: str


class ChatState(TypedDict):
    chat_id: UUID
    messages: list[ChatMessage]
    context: str | None
    confidence: int | None


class apppointmentState(TypedDict):
    name: str
    phone: str
    requested_datetime: str
    available_slots: str
    ok_to_book: bool



