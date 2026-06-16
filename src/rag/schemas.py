from typing import TypedDict, NotRequired

from src.chats.schemas import ChatMessage

class RagState(TypedDict):
    contact_id: str
    user_input: str
    generated_query: NotRequired[str]
    embedded_query: NotRequired[list[float]]
    prompt: NotRequired[str]
    chat_history: list[ChatMessage]
    retrieved_context: NotRequired[str]
    generated_reply: NotRequired[str]
    errors: NotRequired[list[str]]

