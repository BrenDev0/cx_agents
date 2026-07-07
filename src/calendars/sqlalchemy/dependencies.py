from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.db.sqlalchemy.dependencies import get_db_session

from .repository import create, get_by_assistant_id, update_by_assistant_id, delete_by_assistant_id
from ..models import Calendar, CalendarCreate, CalendarUpdate
from ..types import (
    CreateCalendarFn,
    GetCalendarByAssistantIdFn,
    UpdateCalendarByAssistantIdFn,
    DeleteCalendarByAssistantIdFn,
)


def provide_create_calendar(db: AsyncSession = Depends(get_db_session)) -> CreateCalendarFn:
    async def create_calendar(calendar_in: CalendarCreate) -> Calendar:
        return await create(db=db, calendar_in=calendar_in)

    return create_calendar


def provide_get_calendar_by_assistant_id(db: AsyncSession = Depends(get_db_session)) -> GetCalendarByAssistantIdFn:
    async def get_calendar_by_assistant_id(assistant_id: UUID) -> Calendar | None:
        return await get_by_assistant_id(db=db, assistant_id=assistant_id)

    return get_calendar_by_assistant_id


def provide_update_calendar_by_assistant_id(db: AsyncSession = Depends(get_db_session)) -> UpdateCalendarByAssistantIdFn:
    async def update_calendar_by_assistant_id(assistant_id: UUID, calendar_in: CalendarUpdate) -> Calendar | None:
        return await update_by_assistant_id(db=db, assistant_id=assistant_id, calendar_in=calendar_in)

    return update_calendar_by_assistant_id


def provide_delete_calendar_by_assistant_id(db: AsyncSession = Depends(get_db_session)) -> DeleteCalendarByAssistantIdFn:
    async def delete_calendar_by_assistant_id(assistant_id: UUID) -> Calendar | None:
        return await delete_by_assistant_id(db=db, assistant_id=assistant_id)

    return delete_calendar_by_assistant_id
