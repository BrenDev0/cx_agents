from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.db.sqlalchemy.dependencies import get_db_session

from .repository import create, get_by_id, delete_by_id
from ..models import Document, DocumentCreate
from ..types import CreateDocumentFn, GetDocumentByIdFn, DeleteDocumentByIdFn


def provide_create_document(db: AsyncSession = Depends(get_db_session)) ->  CreateDocumentFn:
    async def create_document(document_in: DocumentCreate) -> Document:
        return await create(db=db, document_in=document_in)

    return create_document


def provide_get_document_by_id(db: AsyncSession = Depends(get_db_session)) -> GetDocumentByIdFn:
    async def get_document_by_id(document_id: UUID, user_id: UUID) -> Document | None:
        return await get_by_id(db=db, document_id=document_id, user_id=user_id)

    return get_document_by_id


def provide_delete_document_by_id(db: AsyncSession = Depends(get_db_session)) -> DeleteDocumentByIdFn:
    async def delete_document_by_id(document_id: UUID, user_id: UUID) -> Document | None:
        return await delete_by_id(db=db, document_id=document_id, user_id=user_id)

    return delete_document_by_id