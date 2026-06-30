from dataclasses import asdict

from  ..models import Credential, CredentialPartial
from .models import CredentialRow

def row_to_domain(row: CredentialRow) -> Credential:
    return Credential(
        id=row.id,
        external_id=row.external_id,
        access_token=row.acccess_token,
        created_at=row.created_at
    )

def domain_partial_to_row(partial: CredentialPartial) -> CredentialRow:
    return  CredentialRow(**asdict(partial))
