from uuid import UUID
from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.assistants.types import GetAssistantByIdFn
from src.assistants.sqlalchemy.dependencies import provide_get_assistant_by_id
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService

from .schemas import CreateMessagingCredentialRequest, MessagingCredentialResponse
from .types import (
    CreateMessagingCredentialFn,
    GetMessagingCredentialByIdFn,
    GetMessagingCredentialByAssistantAndChannelFn,
    DeleteMessagingCredentialByIdFn
)
from .sqlalchemy.dependencies import (
    provide_create_messaging_credential,
    provide_get_messaging_credential_by_id,
    provide_get_messaging_credential_by_assistant_and_channel,
    provide_delete_messaging_credential_by_id
)
from .usecases import (
    handle_create_messaging_credential,
    handle_get_messaging_credential,
    handle_delete_messaging_credential
)

router = APIRouter(
    tags=["Messaging Credentials"]
)


@router.post("", status_code=201, response_model=MessagingCredentialResponse)
async def messaging_credentials_create(
    data: CreateMessagingCredentialRequest,
    current_user: User = Depends(get_current_user),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id),
    get_credential_by_assistant_and_channel: GetMessagingCredentialByAssistantAndChannelFn = Depends(
        provide_get_messaging_credential_by_assistant_and_channel
    ),
    create_credential: CreateMessagingCredentialFn = Depends(provide_create_messaging_credential),
    cryptography: CryptographyService = Depends(get_cryptography_service)
):
    return await handle_create_messaging_credential(
        credential_in=data,
        user_id=current_user.id,
        get_assistant_by_id=get_assistant_by_id,
        get_credential_by_assistant_and_channel=get_credential_by_assistant_and_channel,
        create_credential=create_credential,
        encryption=cryptography.encrypt
    )


@router.get("/{credential_id}", response_model=MessagingCredentialResponse)
async def messaging_credentials_get(
    credential_id: UUID,
    current_user: User = Depends(get_current_user),
    get_credential_by_id: GetMessagingCredentialByIdFn = Depends(provide_get_messaging_credential_by_id),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id)
):
    return await handle_get_messaging_credential(
        credential_id=credential_id,
        user_id=current_user.id,
        get_credential_by_id=get_credential_by_id,
        get_assistant_by_id=get_assistant_by_id
    )


@router.delete("/{credential_id}", status_code=204)
async def messaging_credentials_delete(
    credential_id: UUID,
    current_user: User = Depends(get_current_user),
    get_credential_by_id: GetMessagingCredentialByIdFn = Depends(provide_get_messaging_credential_by_id),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id),
    delete_credential_by_id: DeleteMessagingCredentialByIdFn = Depends(provide_delete_messaging_credential_by_id)
):
    await handle_delete_messaging_credential(
        credential_id=credential_id,
        user_id=current_user.id,
        get_credential_by_id=get_credential_by_id,
        get_assistant_by_id=get_assistant_by_id,
        delete_credential_by_id=delete_credential_by_id
    )
