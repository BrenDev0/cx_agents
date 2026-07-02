from datetime import datetime, timezone
from uuid import uuid4

from src.knowledge_base.mappers import domain_to_public_schema
from src.knowledge_base.models import Knowledge, KnowledgeCreate, KnowledgeStatus
from src.knowledge_base.sqlalchemy.mappers import domain_create_to_row, row_to_domain
from src.knowledge_base.sqlalchemy.models import KnowledgeRow


def make_knowledge(**overrides) -> Knowledge:
    defaults = dict(
        id=uuid4(),
        assistant_id=uuid4(),
        document_id=uuid4(),
        status=KnowledgeStatus.READY,
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return Knowledge(**defaults)


def test_domain_to_public_schema_maps_fields():
    knowledge = make_knowledge()

    result = domain_to_public_schema(knowledge)

    assert result.id == knowledge.id
    assert result.assistant_id == knowledge.assistant_id
    assert result.document_id == knowledge.document_id
    assert result.status == KnowledgeStatus.READY
    assert result.created_at == knowledge.created_at


def test_domain_create_to_row_maps_all_fields():
    knowledge_create = KnowledgeCreate(
        assistant_id=uuid4(),
        document_id=uuid4(),
        status=KnowledgeStatus.PENDING
    )

    row = domain_create_to_row(knowledge_create)

    assert isinstance(row, KnowledgeRow)
    assert row.assistant_id == knowledge_create.assistant_id
    assert row.document_id == knowledge_create.document_id
    assert row.status == "pending"


def test_domain_create_to_row_defaults_to_pending_status():
    knowledge_create = KnowledgeCreate(assistant_id=uuid4(), document_id=uuid4())

    row = domain_create_to_row(knowledge_create)

    assert row.status == KnowledgeStatus.PENDING.value


def test_row_to_domain_maps_all_fields():
    row = KnowledgeRow(
        id=uuid4(),
        assistant_id=uuid4(),
        document_id=uuid4(),
        status="ready",
        created_at=datetime.now(timezone.utc)
    )

    domain = row_to_domain(row)

    assert domain == Knowledge(
        id=row.id,
        assistant_id=row.assistant_id,
        document_id=row.document_id,
        status=KnowledgeStatus.READY,
        created_at=row.created_at
    )
