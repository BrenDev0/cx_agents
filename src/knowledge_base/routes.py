from uuid import UUID
from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.documents.types import GetDocumentByIdFn
from src.documents.sqlalchemy.dependencies import provide_get_document_by_id
from src.assistants.types import GetAssistantByIdFn
from src.assistants.sqlalchemy.dependencies import provide_get_assistant_by_id
from src.vector_store.types import VectorStore
from src.vector_store.dependencies import get_vector_store

from .schemas import KnowledgeCreateRequest, KnowledgeResponse
from .types import (
    CreateKnowledgeFn,
    GetKnowledgeByAssistantAndDocumentFn,
    GetKnowledgeByAssistantIdFn,
    GetKnowledgeByIdFn,
    UpdateKnowledgeStatusFn,
    DeleteKnowledgeByIdFn
)
from .sqlalchemy.dependencies import (
    provide_create_knowledge,
    provide_get_knowledge_by_assistant_and_document,
    provide_get_knowledge_by_assistant_id,
    provide_get_knowledge_by_id,
    provide_update_knowledge_status,
    provide_delete_knowledge_by_id
)
from .usecases import (
    handle_create_knowledge,
    handle_list_assistant_knowledge,
    handle_retry_knowledge,
    handle_delete_knowledge
)

router = APIRouter(
    tags=["Knowledge Base"]
)


@router.post("", status_code=202, response_model=KnowledgeResponse)
async def knowledge_create(
    data: KnowledgeCreateRequest,
    current_user: User = Depends(get_current_user),
    get_document_by_id: GetDocumentByIdFn = Depends(provide_get_document_by_id),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id),
    get_knowledge_by_assistant_and_document: GetKnowledgeByAssistantAndDocumentFn = Depends(provide_get_knowledge_by_assistant_and_document),
    create_knowledge: CreateKnowledgeFn = Depends(provide_create_knowledge)
):
    return await handle_create_knowledge(
        document_id=data.document_id,
        assistant_id=data.assistant_id,
        user_id=current_user.id,
        get_document_by_id=get_document_by_id,
        get_assistant_by_id=get_assistant_by_id,
        get_knowledge_by_assistant_and_document=get_knowledge_by_assistant_and_document,
        create_knowledge=create_knowledge
    )


@router.get("/assistant/{assistant_id}", response_model=list[KnowledgeResponse])
async def knowledge_list_by_assistant(
    assistant_id: UUID,
    current_user: User = Depends(get_current_user),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id),
    get_knowledge_by_assistant_id: GetKnowledgeByAssistantIdFn = Depends(provide_get_knowledge_by_assistant_id)
):
    return await handle_list_assistant_knowledge(
        assistant_id=assistant_id,
        user_id=current_user.id,
        get_assistant_by_id=get_assistant_by_id,
        get_knowledge_by_assistant_id=get_knowledge_by_assistant_id
    )


@router.post("/{knowledge_id}/retry", status_code=202, response_model=KnowledgeResponse)
async def knowledge_retry(
    knowledge_id: UUID,
    current_user: User = Depends(get_current_user),
    get_knowledge_by_id: GetKnowledgeByIdFn = Depends(provide_get_knowledge_by_id),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id),
    update_knowledge_status: UpdateKnowledgeStatusFn = Depends(provide_update_knowledge_status)
):
    return await handle_retry_knowledge(
        knowledge_id=knowledge_id,
        user_id=current_user.id,
        get_knowledge_by_id=get_knowledge_by_id,
        get_assistant_by_id=get_assistant_by_id,
        update_knowledge_status=update_knowledge_status
    )


@router.delete("/{knowledge_id}", status_code=204)
async def knowledge_delete(
    knowledge_id: UUID,
    current_user: User = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
    get_knowledge_by_id: GetKnowledgeByIdFn = Depends(provide_get_knowledge_by_id),
    get_assistant_by_id: GetAssistantByIdFn = Depends(provide_get_assistant_by_id),
    delete_knowledge_by_id: DeleteKnowledgeByIdFn = Depends(provide_delete_knowledge_by_id)
):
    await handle_delete_knowledge(
        knowledge_id=knowledge_id,
        user_id=current_user.id,
        vector_store=vector_store,
        get_knowledge_by_id=get_knowledge_by_id,
        get_assistant_by_id=get_assistant_by_id,
        delete_knowledge_by_id=delete_knowledge_by_id
    )
