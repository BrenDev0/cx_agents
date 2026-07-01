from uuid import UUID
from typing import Callable, Awaitable, Protocol
from .models import AssistantSetting, AssistantSettingCreate, AssistantSettingUpdate

CreateAssistantSettingFn = Callable[[AssistantSettingCreate], Awaitable[AssistantSetting]]
GetAssistantSettingByAssistantIdFn = Callable[[UUID], Awaitable[AssistantSetting | None]]
DeleteAssistantSettingByAssistantIdFn = Callable[[UUID], Awaitable[AssistantSetting | None]]


class UpdateAssistantSettingByAssistantIdFn(Protocol):
    async def __call__(self, assistant_id: UUID, assistant_setting_in: AssistantSettingUpdate) -> AssistantSetting | None: ...
