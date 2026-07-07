from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.assistants.models import Assistant
from src.assistants.dependencies import get_owned_assistant

from .schemas import CalendarUpdateRequest, CalendarResponse
from .types import UpdateCalendarByAssistantIdFn, DeleteCalendarByAssistantIdFn
from .sqlalchemy.dependencies import (
    provide_update_calendar_by_assistant_id,
    provide_delete_calendar_by_assistant_id
)
from .usecases import handle_update_calendar, handle_delete_calendar

router = APIRouter(
    tags=["Calendars"]
)


@router.put("/{assistant_id}/calendar", response_model=CalendarResponse)
async def calendar_update(
    data: CalendarUpdateRequest,
    assistant: Assistant = Depends(get_owned_assistant),
    current_user: User = Depends(get_current_user),
    update_calendar_by_assistant_id: UpdateCalendarByAssistantIdFn = Depends(provide_update_calendar_by_assistant_id)
):
    return await handle_update_calendar(
        assistant_id=assistant.id,
        calendar_in=data,
        update_calendar_by_assistant_id=update_calendar_by_assistant_id
    )


@router.delete("/{assistant_id}/calendar", status_code=204)
async def calendar_delete(
    assistant: Assistant = Depends(get_owned_assistant),
    current_user: User = Depends(get_current_user),
    delete_calendar_by_assistant_id: DeleteCalendarByAssistantIdFn = Depends(provide_delete_calendar_by_assistant_id)
):
    await handle_delete_calendar(
        assistant_id=assistant.id,
        delete_calendar_by_assistant_id=delete_calendar_by_assistant_id
    )
