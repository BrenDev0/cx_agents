from datetime import datetime, timezone
from uuid import uuid4

from src.documents.mappers import domain_to_public_schema
from src.documents.models import Document, DocumentCreate
from src.documents.sqlalchemy.mappers import domain_create_to_row, row_to_domain
from src.documents.sqlalchemy.models import DocumentRow


def make_document(**overrides) -> Document:
    defaults = dict(
        id=uuid4(),
        user_id=uuid4(),
        file_type="application/pdf",
        name="report.pdf",
        key="user/123-report.pdf",
        file_size=2048,
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return Document(**defaults)


def test_domain_to_public_schema_maps_fields():
    document = make_document()

    result = domain_to_public_schema(document, url="https://example.com/signed")

    assert result.id == document.id
    assert result.name == document.name
    assert result.file_type == document.file_type
    assert result.url == "https://example.com/signed"
    assert result.file_size == document.file_size
    assert result.created_at == document.created_at


def test_domain_to_public_schema_defaults_url_to_none():
    document = make_document()

    result = domain_to_public_schema(document)

    assert result.url is None


def test_domain_create_to_row_maps_all_fields():
    document_create = DocumentCreate(
        user_id=uuid4(),
        file_type="image/png",
        name="photo.png",
        key="user/456-photo.png",
        file_size=1024
    )

    row = domain_create_to_row(document_create)

    assert isinstance(row, DocumentRow)
    assert row.user_id == document_create.user_id
    assert row.file_type == document_create.file_type
    assert row.name == document_create.name
    assert row.key == document_create.key
    assert row.file_size == document_create.file_size


def test_row_to_domain_maps_all_fields():
    row = DocumentRow(
        id=uuid4(),
        user_id=uuid4(),
        file_type="application/pdf",
        name="report.pdf",
        key="user/123-report.pdf",
        file_size=2048,
        created_at=datetime.now(timezone.utc)
    )

    domain = row_to_domain(row)

    assert domain == Document(
        id=row.id,
        user_id=row.user_id,
        file_type=row.file_type,
        name=row.name,
        key=row.key,
        file_size=row.file_size,
        created_at=row.created_at
    )
