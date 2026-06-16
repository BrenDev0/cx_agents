from typing import TypedDict, Any, NotRequired
from enum import StrEnum

class MessageRole(StrEnum):
    SYSTEM = "system"
    HUMAN = "user"
    AI = "assistant"


class ChatMessage(TypedDict):
    role: MessageRole
    content: str

class ChatState(TypedDict):
    contact_id: str
    llm_provider: str
    llm_model: str
    api_key: str
    incomming_message: str
    chat_history: NotRequired[list[ChatMessage]]
    intent: NotRequired[str]
    final_response: NotRequired[str]
    errors: NotRequired[list[str]]
    

