from typing import Any
from pydantic import BaseModel

from src.messaging.credentials.models import MessagingChannel

class GHLChatRequest(BaseModel):
    contact_id: str
    channel: MessagingChannel
    incoming_message: str