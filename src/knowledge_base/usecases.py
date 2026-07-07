from uuid import UUID

from src.documents.types import GetDocumentByIdFn
from src.assistants.types import GetAssistantByIdFn
from src.vector_store.types import VectorStore
from src.exceptions import NotFoundException, ConflictException, BadRequestException

from .models import KnowledgeCreate, KnowledgeStatus
from .schemas import KnowledgeResponse
from .types import (
    GetKnowledgeByAssistantAndDocumentFn,
    GetKnowledgeByAssistantIdFn,
    CreateKnowledgeFn,
    GetKnowledgeByIdFn,
    UpdateKnowledgeStatusFn,
    DeleteKnowledgeByIdFn
)
from .mappers import domain_to_public_schema
from .celery.tasks import add_document_to_knowledge_base


async def handle_create_knowledge(
    document_id: UUID,
    assistant_id: UUID,
    user_id: UUID,
    get_document_by_id: GetDocumentByIdFn,
    get_assistant_by_id: GetAssistantByIdFn,
    get_knowledge_by_assistant_and_document: GetKnowledgeByAssistantAndDocumentFn,
    create_knowledge: CreateKnowledgeFn
) -> KnowledgeResponse:
    document = await get_document_by_id(document_id=document_id, user_id=user_id)
    if not document:
        raise NotFoundException("Document not found")

    if document.file_type != "application/pdf":
        raise BadRequestException("Only PDF documents can be added to a knowledge base")

    assistant = await get_assistant_by_id(assistant_id=assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Assistant not found")

    existing_knowledge = await get_knowledge_by_assistant_and_document(
        assistant_id=assistant_id,
        document_id=document_id
    )
    if existing_knowledge:
        raise ConflictException("Document has already been added to this assistant's knowledge base")

    knowledge = await create_knowledge(KnowledgeCreate(
        assistant_id=assistant_id,
        document_id=document_id,
        status=KnowledgeStatus.PENDING
    ))

    add_document_to_knowledge_base.delay(
        str(knowledge.id),
        str(document_id),
        str(assistant_id),
        str(user_id)
    )

    return domain_to_public_schema(knowledge)


async def handle_list_assistant_knowledge(
    assistant_id: UUID,
    user_id: UUID,
    get_assistant_by_id: GetAssistantByIdFn,
    get_knowledge_by_assistant_id: GetKnowledgeByAssistantIdFn
) -> list[KnowledgeResponse]:
    assistant = await get_assistant_by_id(assistant_id=assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Assistant not found")

    knowledge_entries = await get_knowledge_by_assistant_id(assistant_id=assistant_id)

    return [domain_to_public_schema(knowledge) for knowledge in knowledge_entries]


async def handle_retry_knowledge(
    knowledge_id: UUID,
    user_id: UUID,
    get_knowledge_by_id: GetKnowledgeByIdFn,
    get_assistant_by_id: GetAssistantByIdFn,
    update_knowledge_status: UpdateKnowledgeStatusFn
) -> KnowledgeResponse:
    knowledge = await get_knowledge_by_id(knowledge_id=knowledge_id)
    if not knowledge:
        raise NotFoundException("Knowledge not found")

    assistant = await get_assistant_by_id(assistant_id=knowledge.assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Assistant not found")

    if knowledge.status == KnowledgeStatus.READY:
        raise ConflictException("Knowledge has already been processed")

    if knowledge.status != KnowledgeStatus.FAILED:
        raise ConflictException("Only failed knowledge can be retried")

    updated_knowledge = await update_knowledge_status(
        knowledge_id=knowledge_id,
        status=KnowledgeStatus.PENDING
    )
    if not updated_knowledge:
        raise NotFoundException("Knowledge not found")

    add_document_to_knowledge_base.delay(
        str(updated_knowledge.id),
        str(updated_knowledge.document_id),
        str(updated_knowledge.assistant_id),
        str(user_id)
    )

    return domain_to_public_schema(updated_knowledge)


async def handle_delete_knowledge(
    knowledge_id: UUID,
    user_id: UUID,
    vector_store: VectorStore,
    get_knowledge_by_id: GetKnowledgeByIdFn,
    get_assistant_by_id: GetAssistantByIdFn,
    delete_knowledge_by_id: DeleteKnowledgeByIdFn
) -> None:
    knowledge = await get_knowledge_by_id(knowledge_id=knowledge_id)
    if not knowledge:
        raise NotFoundException("Knowledge not found")

    assistant = await get_assistant_by_id(assistant_id=knowledge.assistant_id, user_id=user_id)
    if not assistant:
        raise NotFoundException("Assistant not found")

    deleted_knowledge = await delete_knowledge_by_id(knowledge_id=knowledge_id, assistant_id=knowledge.assistant_id)
    if not deleted_knowledge:
        raise NotFoundException("Knowledge not found")

    try:
        await vector_store.delete_by_filter({
            "assistant_id": str(knowledge.assistant_id),
            "document_id": str(knowledge.document_id)
        })
    except Exception as e:
        raise RuntimeError(f"Failed to delete vectors for knowledge '{knowledge_id}'") from e
