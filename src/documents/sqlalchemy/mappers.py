from .models import DocumentRow
from ..models import DocumentCreate, Document
from dataclasses import asdict

def domain_create_to_row(domain_create: DocumentCreate) -> DocumentRow:
    return DocumentRow(**asdict(domain_create))

def row_to_domain(row: DocumentRow) -> Document:
    return Document(
        id=row.id,
        user_id=row.user_id,
        file_type=row.file_type,
        name=row.name,
        url=row.url,
        created_at=row.created_at
    )