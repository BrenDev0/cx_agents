from uuid import UUID
from datetime import datetime

from src.schemas import ApiSchema
from .models import MessagingChannel


class CreateMessagingCredentialRequest(ApiSchema):
    assistant_id: UUID
    channel: MessagingChannel
    credential: str


class MessagingCredentialResponse(ApiSchema):
    id: UUID
    assistant_id: UUID
    channel: MessagingChannel
    created_at: datetime
