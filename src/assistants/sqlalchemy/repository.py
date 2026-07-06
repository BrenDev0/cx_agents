from sqlalchemy import select, delete, update
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Assistant, AssistantCreate
from .mappers import row_to_domain, domain_create_to_row
from .models import AssistantRow


async def create(db: AsyncSession, assistant_in: AssistantCreate) -> Assistant:
    row = domain_create_to_row(assistant_in)
    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_id(db: AsyncSession, assistant_id: UUID, user_id: UUID) -> Assistant | None:
    stmt = select(AssistantRow).where(AssistantRow.id == assistant_id).where(AssistantRow.user_id == user_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def get_by_webhook_id(db: AsyncSession, webhook_id: UUID) -> Assistant | None:
    stmt = select(AssistantRow).where(AssistantRow.webhook_id == webhook_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def collection_by_user_id(db: AsyncSession, user_id: UUID) -> list[Assistant]:
    stmt = select(AssistantRow).where(AssistantRow.user_id == user_id)

    result = await db.execute(stmt)

    rows = result.scalars().all()

    return list(row_to_domain(row) for row in rows)


async def delete_by_id(db: AsyncSession, assistant_id: UUID, user_id: UUID) -> Assistant | None:
    stmt = delete(AssistantRow).where(AssistantRow.id == assistant_id).where(AssistantRow.user_id == user_id).returning(AssistantRow)

    result  = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def update_webhook_secret_hash(db: AsyncSession, assistant_id: UUID, user_id: UUID, webhook_secret_hash: str) -> Assistant | None:
    stmt = (
        update(AssistantRow)
        .where(AssistantRow.id == assistant_id)
        .where(AssistantRow.user_id == user_id)
        .values(webhook_secret_hash=webhook_secret_hash)
        .returning(AssistantRow)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None