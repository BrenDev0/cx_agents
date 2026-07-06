from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.db.sqlalchemy.dependencies import get_db_session
from .repository import create, get_by_id, get_by_assistant_and_channel, delete_by_id
from ..models import MessagingCredential, MessagingCredentialCreate, MessagingChannel
from ..types import (
    CreateMessagingCredentialFn,
    GetMessagingCredentialByIdFn,
    GetMessagingCredentialByAssistantAndChannelFn,
    DeleteMessagingCredentialByIdFn
)


def provide_create_messaging_credential(db: AsyncSession = Depends(get_db_session)) -> CreateMessagingCredentialFn:
    async def create_messaging_credential(credential_in: MessagingCredentialCreate) -> MessagingCredential:
        return await create(db=db, credential_in=credential_in)

    return create_messaging_credential


def provide_get_messaging_credential_by_id(db: AsyncSession = Depends(get_db_session)) -> GetMessagingCredentialByIdFn:
    async def get_messaging_credential_by_id(credential_id: UUID) -> MessagingCredential | None:
        return await get_by_id(db=db, credential_id=credential_id)

    return get_messaging_credential_by_id


def provide_get_messaging_credential_by_assistant_and_channel(
    db: AsyncSession = Depends(get_db_session)
) -> GetMessagingCredentialByAssistantAndChannelFn:
    async def get_messaging_credential_by_assistant_and_channel(
        assistant_id: UUID, channel: MessagingChannel
    ) -> MessagingCredential | None:
        return await get_by_assistant_and_channel(db=db, assistant_id=assistant_id, channel=channel)

    return get_messaging_credential_by_assistant_and_channel


def provide_delete_messaging_credential_by_id(db: AsyncSession = Depends(get_db_session)) -> DeleteMessagingCredentialByIdFn:
    async def delete_messaging_credential_by_id(credential_id: UUID) -> MessagingCredential | None:
        return await delete_by_id(db=db, credential_id=credential_id)

    return delete_messaging_credential_by_id
