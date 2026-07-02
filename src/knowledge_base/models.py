from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import StrEnum


class KnowledgeStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(frozen=True)
class Knowledge:
    id: UUID
    assistant_id: UUID
    document_id: UUID
    status: KnowledgeStatus
    created_at: datetime


@dataclass(frozen=True)
class KnowledgeCreate:
    assistant_id: UUID
    document_id: UUID
    status: KnowledgeStatus = KnowledgeStatus.PENDING
