import secrets
from uuid import UUID

from src.cryptography.types import HashTokenFn
from src.exceptions import NotFoundException

from .models import AssistantCreate
from .schemas import AssistantCreateRequest, AssistantResponse
from .types import CreateAssistantFn, DeleteAssistantById, GetUsersAssistantsFn, UpdateAssistantWebhookSecretHashFn
from .mappers import domain_to_public_schema, domain_to_webhook_secret_schema
from .assistant_settings.models import AssistantSettingCreate
from .assistant_settings.types import CreateAssistantSettingFn
from src.calendars.models import CalendarCreate
from src.calendars.types import CreateCalendarFn


async def handle_create(
    assitant_in: AssistantCreateRequest,
    create_assistant: CreateAssistantFn,
    create_assistant_setting: CreateAssistantSettingFn,
    create_calendar: CreateCalendarFn,
    hash_token: HashTokenFn,
    user_id: UUID
):
    webhook_secret = secrets.token_urlsafe(32)

    domain_create = AssistantCreate(
        user_id=user_id,
        name=assitant_in.name,
        description=assitant_in.description,
        webhook_secret_hash=hash_token(webhook_secret)
    )

    new_assistant = await create_assistant(domain_create)

    await create_assistant_setting(AssistantSettingCreate(assistant_id=new_assistant.id))
    await create_calendar(CalendarCreate(assistant_id=new_assistant.id))

    return domain_to_webhook_secret_schema(new_assistant, webhook_secret=webhook_secret)


async def handle_list_assistants(
    user_id: UUID,
    get_users_assistants: GetUsersAssistantsFn
) -> list[AssistantResponse]:
    assistants = await get_users_assistants(user_id)

    return [domain_to_public_schema(assistant) for assistant in assistants]


async def handle_rotate_webhook_secret(
    assistant_id: UUID,
    user_id: UUID,
    hash_token: HashTokenFn,
    update_assistant_webhook_secret_hash: UpdateAssistantWebhookSecretHashFn
):
    webhook_secret = secrets.token_urlsafe(32)

    updated_assistant = await update_assistant_webhook_secret_hash(
        assistant_id=assistant_id,
        user_id=user_id,
        webhook_secret_hash=hash_token(webhook_secret)
    )

    if not updated_assistant:
        raise NotFoundException("Assistant not found")

    return domain_to_webhook_secret_schema(updated_assistant, webhook_secret=webhook_secret)


async def handle_delete_assistant(
    assistant_id: UUID,
    user_id: UUID,
    delete_assistant_by_id: DeleteAssistantById
) -> None:
    deleted_assistant = await delete_assistant_by_id(assistant_id=assistant_id, user_id=user_id)

    if not deleted_assistant:
        raise NotFoundException("Assistant not found")