from uuid import UUID
from .models import AssistantCreate
from .schemas import AssistantCreateRequest
from .types import CreateAssistantFn
from .mappers import domain_to_public_schema
from .assistant_settings.models import AssistantSettingCreate
from .assistant_settings.types import CreateAssistantSettingFn

async def handle_create(
    assitant_in: AssistantCreateRequest,
    create_assistant: CreateAssistantFn,
    create_assistant_setting: CreateAssistantSettingFn,
    user_id: UUID
):
    domain_create = AssistantCreate(
        user_id=user_id,
        name=assitant_in.name,
        description=assitant_in.description
    )

    new_assistant = await create_assistant(domain_create)

    await create_assistant_setting(AssistantSettingCreate(assistant_id=new_assistant.id))

    return domain_to_public_schema(new_assistant)