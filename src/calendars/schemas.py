from src.schemas import ApiSchema
from uuid import UUID
from datetime import datetime


class CalendarUpdateRequest(ApiSchema):
    calendar_id: str | None
    timezone: str | None
    required_fields: list[str] | None
    title_template: str | None


class CalendarResponse(ApiSchema):
    id: UUID
    assistant_id: UUID
    calendar_id: str | None
    timezone: str | None
    required_fields: list[str] | None
    title_template: str | None
    updated_at: datetime
    created_at: datetime
