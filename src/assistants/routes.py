from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from .schemas import AssistantCreateRequest, AssistantResponse
from .types import CreateAssistantFn
from .sqlalchemy.dependencies import provide_create_assistant
from .usecases import handle_create

router = APIRouter(
    tags=["Assistants"]
)


@router.post("", status_code=201, response_model=AssistantResponse)
async def assistants_create(
    data: AssistantCreateRequest,
    current_user: User = Depends(get_current_user),
    create_assistant: CreateAssistantFn = Depends(provide_create_assistant)
):
    return await handle_create(
        assitant_in=data,
        create_assistant=create_assistant,
        user_id=current_user.id
    )