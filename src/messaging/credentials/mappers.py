from .models import MessagingCredential
from .schemas import MessagingCredentialResponse


def domain_to_public_schema(domain: MessagingCredential) -> MessagingCredentialResponse:
    return MessagingCredentialResponse(
        id=domain.id,
        assistant_id=domain.assistant_id,
        channel=domain.channel,
        created_at=domain.created_at
    )
