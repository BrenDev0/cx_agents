from uuid import UUID
from .models import AssistantCreate
from .schemas import AssistantCreateRequest
from .types import CreateAssistantFn
from .mappers import domain_to_public_schema

async def handle_create(
    assitant_in: AssistantCreateRequest,
    create_assistant: CreateAssistantFn,
    user_id: UUID
):
    domain_create = AssistantCreate(
        user_id=user_id,
        name=assitant_in.name,
        description=assitant_in.description
    )

    new_assistant = await create_assistant(domain_create)

    return domain_to_public_schema(new_assistant)