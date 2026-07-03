from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MessagingCredential, MessagingCredentialCreate, MessagingChannel
from .mappers import row_to_domain, domain_create_to_row
from .models import MessagingCredentialRow


async def create(db: AsyncSession, credential_in: MessagingCredentialCreate) -> MessagingCredential:
    row = domain_create_to_row(credential_in)

    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_id(db: AsyncSession, credential_id: UUID) -> MessagingCredential | None:
    stmt = (
        select(MessagingCredentialRow)
        .where(MessagingCredentialRow.id == credential_id)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def get_by_assistant_and_channel(
    db: AsyncSession,
    assistant_id: UUID,
    channel: MessagingChannel
) -> MessagingCredential | None:
    stmt = (
        select(MessagingCredentialRow)
        .where(MessagingCredentialRow.assistant_id == assistant_id)
        .where(MessagingCredentialRow.channel == channel)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def delete_by_id(db: AsyncSession, credential_id: UUID) -> MessagingCredential | None:
    stmt = (
        delete(MessagingCredentialRow)
        .where(MessagingCredentialRow.id == credential_id)
        .returning(MessagingCredentialRow)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None
