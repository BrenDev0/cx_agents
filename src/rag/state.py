from typing_extensions import NotRequired

from src.states import BaseState, AgentHandoffState


class RagState(BaseState, AgentHandoffState):
    generated_query: NotRequired[str]
    embedded_query: NotRequired[list[float]]
    retrieved_context: NotRequired[str]
    answerable: NotRequired[bool]
    generated_reply: NotRequired[str]

