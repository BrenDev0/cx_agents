from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from enum import StrEnum

class MessagingChannel(StrEnum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"

@dataclass(frozen=True)
class MessagingCredential:
    id: UUID
    assistant_id: UUID
    channel: MessagingChannel
    credential: str
    created_at: datetime


@dataclass(frozen=True)
class MessagingCredentialCreate:
    assistant_id: UUID
    channel: MessagingChannel
    credential: str

