from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class Assistant:
    id: UUID
    user_id: UUID
    name: str
    description: str
    created_at: datetime


@dataclass(frozen=True)
class AssistantCreate:
    user_id: UUID
    name: str
    description: str