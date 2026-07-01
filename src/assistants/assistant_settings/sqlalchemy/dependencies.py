from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.db.sqlalchemy.dependencies import get_db_session

from .repository import create, get_by_assistant_id, update_by_assistant_id, delete_by_assistant_id
from ..models import AssistantSetting, AssistantSettingCreate, AssistantSettingUpdate
from ..types import (
    CreateAssistantSettingFn,
    GetAssistantSettingByAssistantIdFn,
    UpdateAssistantSettingByAssistantIdFn,
    DeleteAssistantSettingByAssistantIdFn,
)


def provide_create_assistant_setting(db: AsyncSession = Depends(get_db_session)) -> CreateAssistantSettingFn:
    async def create_assistant_setting(assistant_setting_in: AssistantSettingCreate) -> AssistantSetting:
        return await create(db=db, assistant_setting_in=assistant_setting_in)

    return create_assistant_setting


def provide_get_assistant_setting_by_assistant_id(db: AsyncSession = Depends(get_db_session)) -> GetAssistantSettingByAssistantIdFn:
    async def get_assistant_setting_by_assistant_id(assistant_id: UUID) -> AssistantSetting | None:
        return await get_by_assistant_id(db=db, assistant_id=assistant_id)

    return get_assistant_setting_by_assistant_id


def provide_update_assistant_setting_by_assistant_id(db: AsyncSession = Depends(get_db_session)) -> UpdateAssistantSettingByAssistantIdFn:
    async def update_assistant_setting_by_assistant_id(assistant_id: UUID, assistant_setting_in: AssistantSettingUpdate) -> AssistantSetting | None:
        return await update_by_assistant_id(db=db, assistant_id=assistant_id, assistant_setting_in=assistant_setting_in)

    return update_assistant_setting_by_assistant_id


def provide_delete_assistant_setting_by_assistant_id(db: AsyncSession = Depends(get_db_session)) -> DeleteAssistantSettingByAssistantIdFn:
    async def delete_assistant_setting_by_assistant_id(assistant_id: UUID) -> AssistantSetting | None:
        return await delete_by_assistant_id(db=db, assistant_id=assistant_id)

    return delete_assistant_setting_by_assistant_id
