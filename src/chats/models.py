from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChatContext:
    assistant_id: UUID
    webhook_secret_hash: str
    credential: str
    has_calendar: bool
    has_rag: bool
