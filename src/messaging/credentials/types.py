from uuid import UUID
from typing import Callable, Awaitable, Protocol
from .models import MessagingCredential, MessagingCredentialCreate, MessagingChannel


CreateMessagingCredentialFn = Callable[[MessagingCredentialCreate], Awaitable[MessagingCredential]]


class GetMessagingCredentialByIdFn(Protocol):
    async def __call__(self, credential_id: UUID) -> MessagingCredential | None: ...


class GetMessagingCredentialByAssistantAndChannelFn(Protocol):
    async def __call__(self, assistant_id: UUID, channel: MessagingChannel) -> MessagingCredential | None: ...


class DeleteMessagingCredentialByIdFn(Protocol):
    async def __call__(self, credential_id: UUID) -> MessagingCredential | None: ...
