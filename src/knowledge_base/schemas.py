from uuid import UUID
from datetime import datetime

from src.schemas import ApiSchema
from .models import KnowledgeStatus


class KnowledgeResponse(ApiSchema):
    id: UUID
    assistant_id: UUID
    document_id: UUID
    status: KnowledgeStatus
    created_at: datetime
