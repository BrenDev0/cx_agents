from typing_extensions import NotRequired

from src.chats.state import BaseState

class RagState(BaseState):
    generated_query: NotRequired[str]
    embedded_query: NotRequired[list[float]]
    prompt: NotRequired[str]
    retrieved_context: NotRequired[str]
    generated_reply: NotRequired[str]

