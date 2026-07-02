from .models import Knowledge
from .schemas import KnowledgeResponse


def domain_to_public_schema(domain: Knowledge) -> KnowledgeResponse:
    return KnowledgeResponse(
        id=domain.id,
        assistant_id=domain.assistant_id,
        document_id=domain.document_id,
        status=domain.status,
        created_at=domain.created_at
    )
