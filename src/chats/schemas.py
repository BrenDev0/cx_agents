from typing import Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    contact_id: str
    incoming_message: str
    chat_history: list[dict[str, Any]] = Field(default_factory=list)