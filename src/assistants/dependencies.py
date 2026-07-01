from uuid import UUID
from fastapi import Depends
from src.auth.dependencies import get_current_user
from src.users.models import User
from src.exceptions import NotFoundException

from .models import Assistant
from .types import GetAssistantByIdFn
from .sqlalchemy.dependencies import provide_get_assistant_by_id


async def get_owned_assistant(
    assistant_id: UUID,
    current_user: User = Depends(get_current_user),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id)
) -> Assistant:
    assistant = await get_assistant_by_id(assistant_id=assistant_id, user_id=current_user.id)

    if not assistant:
        raise NotFoundException("Assistant not found")

    return assistant
