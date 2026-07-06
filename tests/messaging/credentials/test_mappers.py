from datetime import datetime, timezone
from uuid import uuid4

from src.messaging.credentials.mappers import domain_to_public_schema
from src.messaging.credentials.models import MessagingChannel, MessagingCredential, MessagingCredentialCreate
from src.messaging.credentials.sqlalchemy.mappers import domain_create_to_row, row_to_domain
from src.messaging.credentials.sqlalchemy.models import MessagingCredentialRow


def make_credential(**overrides) -> MessagingCredential:
    defaults = dict(
        id=uuid4(),
        assistant_id=uuid4(),
        channel=MessagingChannel.WHATSAPP,
        credential="enc:raw-token",
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return MessagingCredential(**defaults)


def test_domain_to_public_schema_maps_fields():
    credential = make_credential()

    result = domain_to_public_schema(credential)

    assert result.id == credential.id
    assert result.assistant_id == credential.assistant_id
    assert result.channel == credential.channel
    assert result.created_at == credential.created_at


def test_domain_to_public_schema_excludes_raw_credential():
    credential = make_credential()

    result = domain_to_public_schema(credential)

    assert not hasattr(result, "credential")


def test_domain_create_to_row_maps_all_fields():
    credential_create = MessagingCredentialCreate(
        assistant_id=uuid4(),
        channel=MessagingChannel.MESSENGER,
        credential="enc:raw-token"
    )

    row = domain_create_to_row(credential_create)

    assert isinstance(row, MessagingCredentialRow)
    assert row.assistant_id == credential_create.assistant_id
    assert row.channel == credential_create.channel
    assert row.credential == credential_create.credential


def test_row_to_domain_maps_all_fields():
    row = MessagingCredentialRow(
        id=uuid4(),
        assistant_id=uuid4(),
        channel=MessagingChannel.SMS,
        credential="enc:raw-token",
        created_at=datetime.now(timezone.utc)
    )

    domain = row_to_domain(row)

    assert domain == MessagingCredential(
        id=row.id,
        assistant_id=row.assistant_id,
        channel=row.channel,
        credential=row.credential,
        created_at=row.created_at
    )
