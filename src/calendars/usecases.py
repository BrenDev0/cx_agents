from uuid import UUID
from src.exceptions import NotFoundException

from .models import CalendarUpdate
from .schemas import CalendarUpdateRequest, CalendarResponse
from .types import UpdateCalendarByAssistantIdFn, DeleteCalendarByAssistantIdFn
from .mappers import domain_to_public_schema


async def handle_update_calendar(
    assistant_id: UUID,
    calendar_in: CalendarUpdateRequest,
    update_calendar_by_assistant_id: UpdateCalendarByAssistantIdFn
) -> CalendarResponse:
    domain_update = CalendarUpdate(
        calendar_id=calendar_in.calendar_id,
        timezone=calendar_in.timezone
    )

    calendar = await update_calendar_by_assistant_id(
        assistant_id=assistant_id,
        calendar_in=domain_update
    )

    if not calendar:
        raise NotFoundException("Calendar not found")

    return domain_to_public_schema(calendar)


async def handle_delete_calendar(
    assistant_id: UUID,
    delete_calendar_by_assistant_id: DeleteCalendarByAssistantIdFn
) -> None:
    calendar = await delete_calendar_by_assistant_id(assistant_id)

    if not calendar:
        raise NotFoundException("Calendar not found")
