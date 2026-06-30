from src.schemas import ApiSchema
from uuid import UUID
from datetime import datetime

class AssistantCreateRequest(ApiSchema):
    name: str
    description: str


class AssistantResponse(ApiSchema):
    id: UUID
    name: str
    description: str
    created_at: datetime