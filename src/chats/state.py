from typing_extensions import TypedDict, NotRequired
from .intents import IntentDefinition
from .types import ChatMessage


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
