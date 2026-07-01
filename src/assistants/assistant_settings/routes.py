from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.assistants.models import Assistant
from src.assistants.dependencies import get_owned_assistant

from .schemas import AssistantSettingUpdateRequest, AssistantSettingResponse
from .types import UpdateAssistantSettingByAssistantIdFn, DeleteAssistantSettingByAssistantIdFn
from .sqlalchemy.dependencies import (
    provide_update_assistant_setting_by_assistant_id,
    provide_delete_assistant_setting_by_assistant_id
)
from .usecases import handle_update_assistant_setting, handle_delete_assistant_setting

router = APIRouter(
    tags=["Assistant Settings"]
)


@router.put("/{assistant_id}/settings", response_model=AssistantSettingResponse)
async def assistant_settings_update(
    data: AssistantSettingUpdateRequest,
    assistant: Assistant = Depends(get_owned_assistant),
    current_user: User = Depends(get_current_user),
    update_assistant_setting_by_assistant_id: UpdateAssistantSettingByAssistantIdFn = Depends(provide_update_assistant_setting_by_assistant_id)
):
    return await handle_update_assistant_setting(
        assistant_id=assistant.id,
        assistant_setting_in=data,
        update_assistant_setting_by_assistant_id=update_assistant_setting_by_assistant_id
    )


@router.delete("/{assistant_id}/settings", status_code=204)
async def assistant_settings_delete(
    assistant: Assistant = Depends(get_owned_assistant),
    current_user: User = Depends(get_current_user),
    delete_assistant_setting_by_assistant_id: DeleteAssistantSettingByAssistantIdFn = Depends(provide_delete_assistant_setting_by_assistant_id)
):
    await handle_delete_assistant_setting(
        assistant_id=assistant.id,
        delete_assistant_setting_by_assistant_id=delete_assistant_setting_by_assistant_id
    )
