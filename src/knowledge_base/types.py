from uuid import UUID
from typing import Callable, Awaitable, Protocol
from .models import KnowledgeCreate, Knowledge, KnowledgeStatus


CreateKnowledgeFn = Callable[[KnowledgeCreate], Awaitable[Knowledge]]


class GetKnowledgeByIdFn(Protocol):
    async def __call__(self, knowledge_id: UUID) -> Knowledge | None: ...


class GetKnowledgeByAssistantAndDocumentFn(Protocol):
    async def __call__(self, assistant_id: UUID, document_id: UUID) -> Knowledge | None: ...


class UpdateKnowledgeStatusFn(Protocol):
    async def __call__(self, knowledge_id: UUID, status: KnowledgeStatus) -> Knowledge | None: ...


class DeleteKnowledgeByIdFn(Protocol):
    async def __call__(self, knowledge_id: UUID, assistant_id: UUID) -> Knowledge | None: ...
