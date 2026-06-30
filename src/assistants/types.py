from uuid import UUID
from typing import Callable, Awaitable, Protocol
from .models import Assistant, AssistantCreate

CreateAssistantFn = Callable[[AssistantCreate], Awaitable[Assistant]]
GetUsersAssistantsFn = Callable[[UUID], Awaitable[Assistant]]

class GetAssistantByIdFn(Protocol):
    async def __call__(*assistant_id: UUID, user_id: UUID) -> Assistant | None: ...


class DeleteAssistantById(Protocol):
    async def __call__(*assistant_id: UUID, user_id: UUID) -> Assistant | None: ...

