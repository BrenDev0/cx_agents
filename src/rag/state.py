from typing_extensions import NotRequired

from src.states import BaseState, AgentHandoffState


class RagState(BaseState, AgentHandoffState):
    generated_query: NotRequired[str]
    embedded_query: NotRequired[list[float]]
    prompt: NotRequired[str]
    retrieved_context: NotRequired[str]
    generated_reply: NotRequired[str]

