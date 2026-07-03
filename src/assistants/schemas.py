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
    webhook_id: UUID
    created_at: datetime


class AssistantWebhookSecretResponse(AssistantResponse):
    """Returned only right after the secret is generated or rotated -- the
    plaintext is never persisted and can't be retrieved again after this."""
    webhook_secret: str