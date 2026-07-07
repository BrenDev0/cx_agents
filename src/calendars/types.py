from uuid import UUID
from typing import Callable, Awaitable, Protocol
from .models import Calendar, CalendarCreate, CalendarUpdate

CreateCalendarFn = Callable[[CalendarCreate], Awaitable[Calendar]]
GetCalendarByAssistantIdFn = Callable[[UUID], Awaitable[Calendar | None]]
DeleteCalendarByAssistantIdFn = Callable[[UUID], Awaitable[Calendar | None]]


class UpdateCalendarByAssistantIdFn(Protocol):
    async def __call__(self, assistant_id: UUID, calendar_in: CalendarUpdate) -> Calendar | None: ...
