from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from .schemas import AssistantCreateRequest

router = APIRouter(
    tags=["Assistants"]
)


@router.post("", status_code=201)
async def assistants_create(
    data: AssistantCreateRequest,
    current_user: User = Depends(get_current_user)
):
    pass