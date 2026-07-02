from ..models import Knowledge, KnowledgeCreate, KnowledgeStatus
from .models import KnowledgeRow


def domain_create_to_row(domain_create: KnowledgeCreate) -> KnowledgeRow:
    return KnowledgeRow(
        assistant_id=domain_create.assistant_id,
        document_id=domain_create.document_id,
        status=domain_create.status.value
    )


def row_to_domain(row: KnowledgeRow) -> Knowledge:
    return Knowledge(
        id=row.id,
        assistant_id=row.assistant_id,
        document_id=row.document_id,
        status=KnowledgeStatus(row.status),
        created_at=row.created_at
    )
