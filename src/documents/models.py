from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class Document:
    id: UUID
    name: str
    url: str
    created_at: datetime


@dataclass(frozen=True)
class DocumentCreate:
    name: str
    url: str