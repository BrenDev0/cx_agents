from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.db.sqlalchemy.dependencies import get_db_session
from .repository import create, collection_by_user_id, get_by_id, delete_by_id
from ..models import Assistant, AssistantCreate
from ..types import CreateAssistantFn, GetUsersAssistantsFn, GetAssistantByIdFn, DeleteAssistantById


def provide_create_assistant(db: AsyncSession = Depends(get_db_session)) -> CreateAssistantFn:
    async def create_assistant(assistant_in: AssistantCreate) -> Assistant:
        return await create(db=db, assistant_in=assistant_in)

    return create_assistant


def provide_get_assistant_by_id(db: AsyncSession = Depends(get_db_session)) -> GetAssistantByIdFn:
    async def get_assistant_by_id(assistant_id: UUID, user_id: UUID) -> Assistant | None:
        return await get_by_id(db=db, assistant_id=assistant_id, user_id=user_id)

    return get_assistant_by_id


def provide_get_users_assistants(db: AsyncSession = Depends(get_db_session)) -> GetUsersAssistantsFn:
    async def get_users_assistants(user_id: UUID) -> list[Assistant]:
        return await collection_by_user_id(db=db, user_id=user_id)
    
    return get_users_assistants


def  provide_delete_assistant_by_id(db: AsyncSession = Depends(get_db_session)) -> DeleteAssistantById:
    async def delete_assistant_by_id(assistant_id: UUID, user_id: UUID) -> Assistant | None:
        return await delete_by_id(db=db, assistant_id=assistant_id, user_id=user_id)
    
    return delete_assistant_by_id
