from typing import TypedDict, NotRequired
from enum import StrEnum

class MessageRole(StrEnum):
    SYSTEM = "system"
    HUMAN = "user"
    AI = "assistant"


class ChatMessage(TypedDict):
    role: MessageRole
    content: str

class BaseState(TypedDict):
    contact_id: str
    llm_provider: str
    llm_model: str
    api_key: str
    incoming_message: str
    chat_history: NotRequired[list[ChatMessage]]
    errors: NotRequired[list[str]]


class ChatState(BaseState):
    intent: NotRequired[str]
    final_response: NotRequired[str]
    
    

