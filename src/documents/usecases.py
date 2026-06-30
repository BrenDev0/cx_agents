from uuid import UUID, uuid4
from src.object_storage.types import ObjectStore
from src.exceptions import NotFoundException

from .models import Document, DocumentCreate
from .schemas import DocumentResponse
from .types import CreateDocumentFn, GetDocumentByIdFn, DeleteDocumentByIdFn
from .mappers import domain_to_public_schema

async def handle_upload(
    user_id: UUID,
    object_store: ObjectStore,
    create_document: CreateDocumentFn,
    filename: str,
    content_type: str,
    file_bytes: bytes
) -> Document:
    object_key = f"{user_id}/{uuid4()}-{filename}"

    document_in = DocumentCreate(
        user_id=user_id,
        file_type=content_type,
        name=filename,
        key=object_key,
        file_size=len(file_bytes)
    )

    document = await create_document(document_in)

    try:
        await object_store.upload(key=object_key, file_bytes=file_bytes)
    except Exception as e:
        raise RuntimeError(f"Failed to upload document '{filename}' to storage") from e

    return domain_to_public_schema(document)


async def handle_get_document(
    document_id: UUID,
    user_id: UUID,
    object_store: ObjectStore,
    get_document_by_id: GetDocumentByIdFn
) -> DocumentResponse:
    document = await get_document_by_id(document_id=document_id, user_id=user_id)

    if not document:
        raise NotFoundException("Document not found")

    url = await object_store.get_object(key=document.key)

    return DocumentResponse(
        id=document.id,
        name=document.name,
        file_type=document.file_type,
        url=url,
        file_size=document.file_size,
        created_at=document.created_at
    )


async def handle_delete_document(
    document_id: UUID,
    user_id: UUID,
    object_store: ObjectStore,
    delete_document_by_id: DeleteDocumentByIdFn
) -> None:
    document = await delete_document_by_id(document_id=document_id, user_id=user_id)

    if not document:
        raise NotFoundException("Document not found")

    try:
        await object_store.delete_object(key=document.key)
    except Exception as e:
        raise RuntimeError(f"Failed to delete document '{document.name}' from storage") from e
