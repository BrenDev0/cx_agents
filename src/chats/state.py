from typing_extensions import TypedDict, NotRequired
from .intents import IntentDefinition, IntentStructure
from .types import ChatMessage


class BaseState(TypedDict):
    contact_id: str
    incoming_message: str
    chat_history: NotRequired[list[ChatMessage]]
    errors: NotRequired[list[str]]

class ChatState(BaseState):
    channel: str
    outgoing_message_id: NotRequired[str]
    available_intents: dict[str, IntentDefinition]
    identified_intent: NotRequired[str]
    next_agent_instructions: NotRequired[str]
    next_agent_context: NotRequired[str]
    final_response: NotRequired[str]
