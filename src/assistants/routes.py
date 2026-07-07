from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService

from .models import Assistant
from .dependencies import get_owned_assistant
from .schemas import AssistantCreateRequest, AssistantResponse, AssistantWebhookSecretResponse
from .types import CreateAssistantFn, DeleteAssistantById, GetUsersAssistantsFn, UpdateAssistantWebhookSecretHashFn
from .sqlalchemy.dependencies import (
    provide_create_assistant,
    provide_delete_assistant_by_id,
    provide_get_users_assistants,
    provide_update_assistant_webhook_secret_hash
)
from .usecases import handle_create, handle_delete_assistant, handle_list_assistants, handle_rotate_webhook_secret
from .assistant_settings.types import CreateAssistantSettingFn
from .assistant_settings.sqlalchemy.dependencies import provide_create_assistant_setting
from src.calendars.types import CreateCalendarFn
from src.calendars.sqlalchemy.dependencies import provide_create_calendar

router = APIRouter(
    tags=["Assistants"]
)


@router.post("", status_code=201, response_model=AssistantWebhookSecretResponse)
async def assistants_create(
    data: AssistantCreateRequest,
    current_user: User = Depends(get_current_user),
    create_assistant: CreateAssistantFn = Depends(provide_create_assistant),
    create_assistant_setting: CreateAssistantSettingFn = Depends(provide_create_assistant_setting),
    create_calendar: CreateCalendarFn = Depends(provide_create_calendar),
    cryptography: CryptographyService = Depends(get_cryptography_service)
):
    return await handle_create(
        assitant_in=data,
        create_assistant=create_assistant,
        create_assistant_setting=create_assistant_setting,
        create_calendar=create_calendar,
        hash_token=cryptography.hash_token,
        user_id=current_user.id
    )


@router.get("", response_model=list[AssistantResponse])
async def assistants_list(
    current_user: User = Depends(get_current_user),
    get_users_assistants: GetUsersAssistantsFn = Depends(provide_get_users_assistants)
):
    return await handle_list_assistants(
        user_id=current_user.id,
        get_users_assistants=get_users_assistants
    )


@router.post("/{assistant_id}/webhook/rotate", response_model=AssistantWebhookSecretResponse)
async def assistants_rotate_webhook_secret(
    assistant: Assistant = Depends(get_owned_assistant),
    current_user: User = Depends(get_current_user),
    update_assistant_webhook_secret_hash: UpdateAssistantWebhookSecretHashFn = Depends(
        provide_update_assistant_webhook_secret_hash
    ),
    cryptography: CryptographyService = Depends(get_cryptography_service)
):
    return await handle_rotate_webhook_secret(
        assistant_id=assistant.id,
        user_id=current_user.id,
        hash_token=cryptography.hash_token,
        update_assistant_webhook_secret_hash=update_assistant_webhook_secret_hash
    )


@router.delete("/{assistant_id}", status_code=204)
async def assistants_delete(
    assistant: Assistant = Depends(get_owned_assistant),
    current_user: User = Depends(get_current_user),
    delete_assistant_by_id: DeleteAssistantById = Depends(provide_delete_assistant_by_id)
):
    await handle_delete_assistant(
        assistant_id=assistant.id,
        user_id=current_user.id,
        delete_assistant_by_id=delete_assistant_by_id
    )