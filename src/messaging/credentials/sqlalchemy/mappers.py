from dataclasses import asdict
from .models import MessagingCredentialRow
from ..models import MessagingCredential, MessagingCredentialCreate

def row_to_domain(row: MessagingCredentialRow) -> MessagingCredential:
    return MessagingCredential(
        id=row.id,
        assistant_id=row.assistant_id,
        channel=row.channel,
        credential=row.credential,
        created_at=row.created_at
    )

def domain_create_to_row(domain_create: MessagingCredentialCreate) -> MessagingCredentialRow:
    return MessagingCredentialRow(**asdict(domain_create))

