from typing_extensions import NotRequired
from .intents import IntentDefinition
from src.states import BaseState, AgentHandoffState


class ChatState(BaseState, AgentHandoffState):
    channel: str
    outgoing_message_id: NotRequired[str]
    available_intents: dict[str, IntentDefinition]
    identified_intent: NotRequired[str]
    final_response: NotRequired[str]
