from sqlalchemy import delete
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Document, DocumentCreate
from .mappers import domain_create_to_row, row_to_domain
from .models import DocumentRow

async def create(db: AsyncSession, document_in: DocumentCreate) -> Document:
    row = domain_create_to_row(document_in)

    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def delete_by_id(db: AsyncSession, id: UUID) ->  Document | None:
    stmt = delete(DocumentRow).where(DocumentRow.id == id).returning(DocumentRow)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None