from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import IntegrationCredentialRow
from ..models import CredentialCreate, Credential, Provider
from .mappers import row_to_domain, domain_create_to_row


async def create(
    db: AsyncSession,
    credential_in: CredentialCreate
) -> Credential:
    row = domain_create_to_row(credential_in)

    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_provider_external_id(
    db: AsyncSession,
    provider: Provider,
    external_id: str,
) -> Credential | None:
    stmt = select(IntegrationCredentialRow).where(
        IntegrationCredentialRow.provider == provider.value,
        IntegrationCredentialRow.external_id == external_id
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None
