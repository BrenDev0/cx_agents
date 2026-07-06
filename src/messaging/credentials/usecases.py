from uuid import UUID

from src.assistants.types import GetAssistantByIdFn
from src.cryptography.types import EncryptFn
from src.exceptions import NotFoundException, ConflictException

from .models import MessagingCredentialCreate
from .schemas import CreateMessagingCredentialRequest, MessagingCredentialResponse
from .types import (
    CreateMessagingCredentialFn,
    GetMessagingCredentialByIdFn,
    GetMessagingCredentialByAssistantAndChannelFn,
    DeleteMessagingCredentialByIdFn
)
from .mappers import domain_to_public_schema


async def handle_create_messaging_credential(
    credential_in: CreateMessagingCredentialRequest,
    user_id: UUID,
    get_assistant_by_id: GetAssistantByIdFn,
    get_credential_by_assistant_and_channel: GetMessagingCredentialByAssistantAndChannelFn,
    create_credential: CreateMessagingCredentialFn,
    encryption: EncryptFn
) -> MessagingCredentialResponse:
    assistant = await get_assistant_by_id(assistant_id=credential_in.assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Assistant not found")

    existing_credential = await get_credential_by_assistant_and_channel(
        assistant_id=credential_in.assistant_id,
        channel=credential_in.channel
    )
    if existing_credential:
        raise ConflictException(f"A {credential_in.channel} credential already exists for this assistant")

    prepared_data = MessagingCredentialCreate(
        assistant_id=credential_in.assistant_id,
        channel=credential_in.channel,
        credential=encryption(credential_in.credential)
    )

    new_credential = await create_credential(prepared_data)

    return domain_to_public_schema(new_credential)


async def handle_get_messaging_credential(
    credential_id: UUID,
    user_id: UUID,
    get_credential_by_id: GetMessagingCredentialByIdFn,
    get_assistant_by_id: GetAssistantByIdFn
) -> MessagingCredentialResponse:
    credential = await get_credential_by_id(credential_id=credential_id)
    if not credential:
        raise NotFoundException("Messaging credential not found")

    assistant = await get_assistant_by_id(assistant_id=credential.assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Messaging credential not found")

    return domain_to_public_schema(credential)


async def handle_delete_messaging_credential(
    credential_id: UUID,
    user_id: UUID,
    get_credential_by_id: GetMessagingCredentialByIdFn,
    get_assistant_by_id: GetAssistantByIdFn,
    delete_credential_by_id: DeleteMessagingCredentialByIdFn
) -> None:
    credential = await get_credential_by_id(credential_id=credential_id)
    if not credential:
        raise NotFoundException("Messaging credential not found")

    assistant = await get_assistant_by_id(assistant_id=credential.assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Messaging credential not found")

    deleted = await delete_credential_by_id(credential_id=credential_id)
    if not deleted:
        raise NotFoundException("Messaging credential not found")
