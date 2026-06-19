from typing_extensions import TypedDict, NotRequired
from typing import Any
from enum import StrEnum
from pydantic import BaseModel, Field

class MessageRole(StrEnum):
    SYSTEM = "system"
    HUMAN = "user"
    AI = "assistant"

class IntentDefinition(TypedDict):
    description: str

class ChatMessage(TypedDict):
    role: MessageRole
    content: str

class BaseState(TypedDict):
    contact_id: str
    pit: str
    incoming_message: str
    chat_history: NotRequired[list[ChatMessage]]
    errors: NotRequired[list[str]]

class ChatState(BaseState):
    available_intents: dict[str, IntentDefinition]
    identified_intent: NotRequired[str]
    final_response: NotRequired[str]


class ChatRequest(BaseModel):
    contact_id: str
    channel: str
    pit: str
    incoming_message: str
    chat_history: list[dict[str, Any]] = Field(default_factory=list)
    activate_appointments: bool
    activate_rag: bool