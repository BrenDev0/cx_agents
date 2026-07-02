from dataclasses import dataclass
from uuid import UUID
from datetime import datetime



@dataclass(frozen=True)
class Knowledge:
    id: UUID
    document_id: UUID
    created_at: datetime


@dataclass(frozen=True)
class KnowledgeCreate:
    document_id: UUID
