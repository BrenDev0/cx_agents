from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import CredentialRow
from..models import CredentialPartial, Credential
from .mappers import row_to_domain, domain_partial_to_row


async def create(
    db: AsyncSession,
    credential_in: CredentialPartial
) -> Credential:
    row = domain_partial_to_row(credential_in)

    await db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_external_id(
    db: AsyncSession,
    external_id: str,
) -> Credential | None:
    stmt = select(CredentialRow).where(CredentialRow.external_id == external_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None
    