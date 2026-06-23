from typing import Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    contact_id: str
    channel: str
    pit: str
    incoming_message: str
    chat_history: list[dict[str, Any]] = Field(default_factory=list)
    activate_appointments: bool
    activate_rag: bool