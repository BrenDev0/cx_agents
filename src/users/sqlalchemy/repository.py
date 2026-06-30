from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..models import UserCreate, User
from .mappers import row_to_domain, domain_create_to_row
from .models import UserRow


async def create(db: AsyncSession, user_in: UserCreate) -> User:
    row = domain_create_to_row(user_in)

    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    stmt = select(UserRow).where(UserRow.id == user_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def get_by_email_hash(db: AsyncSession, email_hash: str) -> User | None:
    stmt = select(UserRow).where(UserRow.email_hash == email_hash)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None