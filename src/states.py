from typing_extensions import TypedDict, NotRequired
from .types import ChatMessage

class BaseState(TypedDict):
    assistant_id: str
    contact_id: str
    channel: str
    credential: str
    incoming_message: str
    chat_history: NotRequired[list[ChatMessage]]
    errors: NotRequired[list[str]]
    prompt: NotRequired[str]

class AgentHandoffState(TypedDict):
    next_agent_instructions: NotRequired[str]
    next_agent_context: NotRequired[str]