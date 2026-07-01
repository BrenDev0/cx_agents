from ..models import Credential, CredentialCreate, Provider
from .models import IntegrationCredentialRow

def row_to_domain(row: IntegrationCredentialRow) -> Credential:
    return Credential(
        id=row.id,
        assistant_id=row.assistant_id,
        provider=Provider(row.provider),
        external_id=row.external_id,
        payload=row.payload,
        expires_at=row.expires_at,
        revoked_at=row.revoked_at,
        created_at=row.created_at
    )

def domain_create_to_row(domain_create: CredentialCreate) -> IntegrationCredentialRow:
    return IntegrationCredentialRow(
        assistant_id=domain_create.assistant_id,
        provider=domain_create.provider.value,
        external_id=domain_create.external_id,
        payload=domain_create.payload,
        expires_at=domain_create.expires_at
    )
