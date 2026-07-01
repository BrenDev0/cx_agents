from src.schemas import ApiSchema
from uuid import UUID
from datetime import datetime


class AssistantSettingUpdateRequest(ApiSchema):
    personality: str
    instructions: str
    rules: str
    has_calendar: bool
    has_rag: bool


class AssistantSettingResponse(ApiSchema):
    id: UUID
    assistant_id: UUID
    personality: str
    instructions: str
    rules: str
    has_calendar: bool
    has_rag: bool
    updated_at: datetime
    created_at: datetime
