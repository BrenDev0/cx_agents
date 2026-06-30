from uuid import UUID
from typing import Callable, Awaitable, Protocol
from .models import DocumentCreate, Document


CreateDocumentFn = Callable[[DocumentCreate], Awaitable[Document]]


class GetDocumentByIdFn(Protocol):
    async def __call__(self, document_id: UUID, user_id: UUID) -> Document | None: ...


class DeleteDocumentByIdFn(Protocol):
    async def __call__(self, document_id: UUID, user_id: UUID) -> Document | None: ...
