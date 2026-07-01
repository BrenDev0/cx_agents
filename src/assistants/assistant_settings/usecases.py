from uuid import UUID
from src.exceptions import NotFoundException

from .models import AssistantSettingUpdate
from .schemas import AssistantSettingUpdateRequest, AssistantSettingResponse
from .types import UpdateAssistantSettingByAssistantIdFn, DeleteAssistantSettingByAssistantIdFn
from .mappers import domain_to_public_schema


async def handle_update_assistant_setting(
    assistant_id: UUID,
    assistant_setting_in: AssistantSettingUpdateRequest,
    update_assistant_setting_by_assistant_id: UpdateAssistantSettingByAssistantIdFn
) -> AssistantSettingResponse:
    domain_update = AssistantSettingUpdate(
        personality=assistant_setting_in.personality,
        instructions=assistant_setting_in.instructions,
        rules=assistant_setting_in.rules,
        has_calendar=assistant_setting_in.has_calendar,
        has_rag=assistant_setting_in.has_rag
    )

    assistant_setting = await update_assistant_setting_by_assistant_id(
        assistant_id=assistant_id,
        assistant_setting_in=domain_update
    )

    if not assistant_setting:
        raise NotFoundException("Assistant setting not found")

    return domain_to_public_schema(assistant_setting)


async def handle_delete_assistant_setting(
    assistant_id: UUID,
    delete_assistant_setting_by_assistant_id: DeleteAssistantSettingByAssistantIdFn
) -> None:
    assistant_setting = await delete_assistant_setting_by_assistant_id(
        assistant_id=assistant_id
    )

    if not assistant_setting:
        raise NotFoundException("Assistant setting not found")
