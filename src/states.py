from typing_extensions import TypedDict, NotRequired
from .types import ChatMessage

class BaseState(TypedDict):
    contact_id: str
    incoming_message: str
    chat_history: NotRequired[list[ChatMessage]]
    errors: NotRequired[list[str]]

class AgentHandoffState(TypedDict):
    next_agent_instructions: NotRequired[str]
    next_agent_context: NotRequired[str]