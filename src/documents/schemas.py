from src.schemas import ApiSchema
from uuid import UUID
from datetime import datetime


class DocumentResponse(ApiSchema):
    id: UUID
    name: str
    file_type: str
    url: str | None
    file_size: int
    created_at: datetime