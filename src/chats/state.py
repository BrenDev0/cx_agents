from typing_extensions import NotRequired
from .intents import IntentDefinition
from src.states import BaseState, AgentHandoffState


class ChatState(BaseState, AgentHandoffState):
    outgoing_message_id: NotRequired[str]
    available_intents: dict[str, IntentDefinition]
    identified_intent: NotRequired[str]
    final_response: NotRequired[str]
    calendar_id: NotRequired[str | None]
    timezone: NotRequired[str | None]
    required_fields: NotRequired[list[str] | None]
    title_template: NotRequired[str | None]
