from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class Calendar:
    id: UUID
    assistant_id: UUID
    calendar_id: str | None
    timezone: str | None
    required_fields: list[str] | None
    title_template: str | None
    updated_at: datetime
    created_at: datetime

@dataclass(frozen=True)
class CalendarCreate:
    assistant_id: UUID
    calendar_id: str | None = None
    timezone: str | None = None
    required_fields: list[str] | None = None
    title_template: str | None = None

@dataclass(frozen=True)
class CalendarUpdate:
    calendar_id: str | None
    timezone: str | None
    required_fields: list[str] | None
    title_template: str | None
