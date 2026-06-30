from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class Document:
    id: UUID
    user_id: UUID
    file_type: str
    name: str
    url: str
    created_at: datetime


@dataclass(frozen=True)
class DocumentCreate:
    user_id: UUID
    file_type: str
    name: str
    url: str