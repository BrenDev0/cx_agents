from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService

from .models import Assistant
from .dependencies import get_owned_assistant
from .schemas import AssistantCreateRequest, AssistantWebhookSecretResponse
from .types import CreateAssistantFn, UpdateAssistantWebhookSecretHashFn
from .sqlalchemy.dependencies import provide_create_assistant, provide_update_assistant_webhook_secret_hash
from .usecases import handle_create, handle_rotate_webhook_secret
from .assistant_settings.types import CreateAssistantSettingFn
from .assistant_settings.sqlalchemy.dependencies import provide_create_assistant_setting

router = APIRouter(
    tags=["Assistants"]
)


@router.post("", status_code=201, response_model=AssistantWebhookSecretResponse)
async def assistants_create(
    data: AssistantCreateRequest,
    current_user: User = Depends(get_current_user),
    create_assistant: CreateAssistantFn = Depends(provide_create_assistant),
    create_assistant_setting: CreateAssistantSettingFn = Depends(provide_create_assistant_setting),
    cryptography: CryptographyService = Depends(get_cryptography_service)
):
    return await handle_create(
        assitant_in=data,
        create_assistant=create_assistant,
        create_assistant_setting=create_assistant_setting,
        hash_token=cryptography.hash_token,
        user_id=current_user.id
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