from uuid import UUID

from src.documents.types import GetDocumentByIdFn
from src.assistants.types import GetAssistantByIdFn
from src.exceptions import NotFoundException, ConflictException, BadRequestException

from .models import KnowledgeCreate, KnowledgeStatus
from .schemas import KnowledgeResponse
from .types import GetKnowledgeByAssistantAndDocumentFn, CreateKnowledgeFn
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
