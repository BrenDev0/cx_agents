from uuid import UUID
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Knowledge, KnowledgeCreate, KnowledgeStatus
from .mappers import domain_create_to_row, row_to_domain
from .models import KnowledgeRow


async def create(db: AsyncSession, knowledge_in: KnowledgeCreate) -> Knowledge:
    row = domain_create_to_row(knowledge_in)

    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_id(db: AsyncSession, knowledge_id: UUID, assistant_id: UUID) -> Knowledge | None:
    stmt = select(KnowledgeRow).where(KnowledgeRow.id == knowledge_id).where(KnowledgeRow.assistant_id == assistant_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def get_by_assistant_and_document(db: AsyncSession, assistant_id: UUID, document_id: UUID) -> Knowledge | None:
    stmt = select(KnowledgeRow).where(KnowledgeRow.assistant_id == assistant_id).where(KnowledgeRow.document_id == document_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def update_status(db: AsyncSession, knowledge_id: UUID, status: KnowledgeStatus) -> Knowledge | None:
    stmt = (
        update(KnowledgeRow)
        .where(KnowledgeRow.id == knowledge_id)
        .values(status=status.value)
        .returning(KnowledgeRow)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def delete_by_id(db: AsyncSession, knowledge_id: UUID, assistant_id: UUID) -> Knowledge | None:
    stmt = delete(KnowledgeRow).where(KnowledgeRow.id == knowledge_id).where(KnowledgeRow.assistant_id == assistant_id).returning(KnowledgeRow)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None
