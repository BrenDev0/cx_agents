from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from src.db.sqlalchemy.dependencies import get_db_session
from .repository import create, get_by_id, get_by_assistant_and_document, update_status, delete_by_id
from ..types import (
    CreateKnowledgeFn,
    GetKnowledgeByIdFn,
    GetKnowledgeByAssistantAndDocumentFn,
    UpdateKnowledgeStatusFn,
    DeleteKnowledgeByIdFn
)
from ..models import Knowledge, KnowledgeCreate, KnowledgeStatus


def provide_create_knowledge(db: AsyncSession = Depends(get_db_session)) -> CreateKnowledgeFn:
    async def create_knowledge(knowledge_in: KnowledgeCreate) -> Knowledge:
        return await create(db=db, knowledge_in=knowledge_in)

    return create_knowledge


def provide_get_knowledge_by_id(db: AsyncSession = Depends(get_db_session)) -> GetKnowledgeByIdFn:
    async def get_knowledge_by_id(knowledge_id: UUID, assistant_id: UUID) -> Knowledge | None:
        return await get_by_id(db=db, knowledge_id=knowledge_id, assistant_id=assistant_id)

    return get_knowledge_by_id


def provide_get_knowledge_by_assistant_and_document(
    db: AsyncSession = Depends(get_db_session)
) -> GetKnowledgeByAssistantAndDocumentFn:
    async def get_knowledge_by_assistant_and_document(assistant_id: UUID, document_id: UUID) -> Knowledge | None:
        return await get_by_assistant_and_document(db=db, assistant_id=assistant_id, document_id=document_id)

    return get_knowledge_by_assistant_and_document


def provide_update_knowledge_status(db: AsyncSession = Depends(get_db_session)) -> UpdateKnowledgeStatusFn:
    async def update_knowledge_status(knowledge_id: UUID, status: KnowledgeStatus) -> Knowledge | None:
        return await update_status(db=db, knowledge_id=knowledge_id, status=status)

    return update_knowledge_status


def provide_delete_knowledge_by_id(db: AsyncSession = Depends(get_db_session)) -> DeleteKnowledgeByIdFn:
    async def delete_knowledge_by_id(knowledge_id: UUID, assistant_id: UUID) -> Knowledge | None:
        return await delete_by_id(db=db, knowledge_id=knowledge_id, assistant_id=assistant_id)

    return delete_knowledge_by_id
