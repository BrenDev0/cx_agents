from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.object_storage.types import ObjectStore
from src.object_storage.dependencies import get_object_store

from .schemas import DocumentResponse
from .types import CreateDocumentFn, GetDocumentByIdFn, DeleteDocumentByIdFn
from .sqlalchemy.dependencies import (
    provide_create_document,
    provide_get_document_by_id,
    provide_delete_document_by_id
)
from .usecases import handle_upload, handle_get_document, handle_delete_document
from .mappers import domain_to_public_schema

router = APIRouter(
    tags=["Documents"]
)


@router.post("", status_code=201, response_model=DocumentResponse)
async def documents_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    object_store: ObjectStore = Depends(get_object_store),
    create_document: CreateDocumentFn = Depends(provide_create_document)
):
    file_bytes = await file.read()

    return await handle_upload(
        user_id=current_user.id,
        object_store=object_store,
        create_document=create_document,
        filename=file.filename or "untitled",
        content_type=file.content_type or "application/octet-stream",
        file_bytes=file_bytes
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def documents_get(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    object_store: ObjectStore = Depends(get_object_store),
    get_document_by_id: GetDocumentByIdFn = Depends(provide_get_document_by_id)
):
    return await handle_get_document(
        document_id=document_id,
        user_id=current_user.id,
        object_store=object_store,
        get_document_by_id=get_document_by_id
    )


@router.delete("/{document_id}", status_code=204)
async def documents_delete(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    object_store: ObjectStore = Depends(get_object_store),
    delete_document_by_id: DeleteDocumentByIdFn = Depends(provide_delete_document_by_id)
):
    await handle_delete_document(
        document_id=document_id,
        user_id=current_user.id,
        object_store=object_store,
        delete_document_by_id=delete_document_by_id
    )
