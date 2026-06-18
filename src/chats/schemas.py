from typing_extensions import TypedDict, NotRequired
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


class AcceptedChannels(StrEnum):
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"

class ChatRequest(BaseModel):
    contact_id: str
    channel: AcceptedChannels
    pit: str
    incoming_message: str
    chat_history: list[ChatMessage] = Field(default_factory=list)
    activate_appointments: bool
    activate_rag: bool



class ChatTaskPayload(TypedDict):
    state: ChatState
    ok_to_reply: bool