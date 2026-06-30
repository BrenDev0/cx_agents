from .models import Document
from .schemas import DocumentResponse


def domain_to_public_schema(domain: Document, url: str | None = None) -> DocumentResponse:
    return DocumentResponse(
        id=domain.id,
        name=domain.name,
        file_type=domain.file_type,
        url=url,
        file_size=domain.file_size,
        created_at=domain.created_at
    )
