from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.assistants.models import Assistant
from src.exceptions import ConflictException, NotFoundException
from src.messaging.credentials.models import MessagingChannel, MessagingCredential, MessagingCredentialCreate
from src.messaging.credentials.schemas import CreateMessagingCredentialRequest
from src.messaging.credentials.usecases import (
    handle_create_messaging_credential,
    handle_delete_messaging_credential,
    handle_get_messaging_credential
)


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


def make_assistant(**overrides) -> Assistant:
    defaults = dict(
        id=uuid4(),
        user_id=uuid4(),
        name="Support bot",
        description="Handles support tickets",
        webhook_id=uuid4(),
        webhook_secret_hash="test-secret-hash",
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return Assistant(**defaults)


async def unexpected(*args, **kwargs):
    raise AssertionError("should not be called")


async def test_handle_create_messaging_credential_encrypts_and_creates(fake_cryptography_service):
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    created: dict[str, MessagingCredentialCreate] = {}

    data = CreateMessagingCredentialRequest(
        assistant_id=assistant.id,
        channel=MessagingChannel.WHATSAPP,
        credential="raw-token"
    )

    async def fake_get_assistant_by_id(assistant_id, user_id):
        assert assistant_id == assistant.id
        return assistant

    async def fake_get_credential_by_assistant_and_channel(assistant_id, channel):
        return None

    async def fake_create_credential(credential_in: MessagingCredentialCreate) -> MessagingCredential:
        created["credential_in"] = credential_in
        return make_credential(
            assistant_id=credential_in.assistant_id,
            channel=credential_in.channel,
            credential=credential_in.credential
        )

    response = await handle_create_messaging_credential(
        credential_in=data,
        user_id=user_id,
        get_assistant_by_id=fake_get_assistant_by_id,
        get_credential_by_assistant_and_channel=fake_get_credential_by_assistant_and_channel,
        create_credential=fake_create_credential,
        encryption=fake_cryptography_service.encrypt
    )

    assert response.assistant_id == assistant.id
    assert response.channel == MessagingChannel.WHATSAPP
    assert created["credential_in"].credential == fake_cryptography_service.encrypt("raw-token")
    assert not hasattr(response, "credential")


async def test_handle_create_messaging_credential_raises_when_assistant_not_found(fake_cryptography_service):
    data = CreateMessagingCredentialRequest(
        assistant_id=uuid4(),
        channel=MessagingChannel.SMS,
        credential="raw-token"
    )

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_create_messaging_credential(
            credential_in=data,
            user_id=uuid4(),
            get_assistant_by_id=fake_get_assistant_by_id,
            get_credential_by_assistant_and_channel=unexpected,
            create_credential=unexpected,
            encryption=fake_cryptography_service.encrypt
        )


async def test_handle_create_messaging_credential_raises_when_channel_already_exists(fake_cryptography_service):
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    existing = make_credential(assistant_id=assistant.id, channel=MessagingChannel.SMS)

    data = CreateMessagingCredentialRequest(
        assistant_id=assistant.id,
        channel=MessagingChannel.SMS,
        credential="raw-token"
    )

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return assistant

    async def fake_get_credential_by_assistant_and_channel(assistant_id, channel):
        return existing

    with pytest.raises(ConflictException):
        await handle_create_messaging_credential(
            credential_in=data,
            user_id=user_id,
            get_assistant_by_id=fake_get_assistant_by_id,
            get_credential_by_assistant_and_channel=fake_get_credential_by_assistant_and_channel,
            create_credential=unexpected,
            encryption=fake_cryptography_service.encrypt
        )


async def test_handle_get_messaging_credential_returns_response_when_owned():
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    credential = make_credential(assistant_id=assistant.id)

    async def fake_get_credential_by_id(credential_id):
        assert credential_id == credential.id
        return credential

    async def fake_get_assistant_by_id(assistant_id, user_id):
        assert assistant_id == assistant.id
        return assistant

    response = await handle_get_messaging_credential(
        credential_id=credential.id,
        user_id=user_id,
        get_credential_by_id=fake_get_credential_by_id,
        get_assistant_by_id=fake_get_assistant_by_id
    )

    assert response.id == credential.id
    assert response.channel == credential.channel


async def test_handle_get_messaging_credential_raises_when_credential_not_found():
    async def fake_get_credential_by_id(credential_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_get_messaging_credential(
            credential_id=uuid4(),
            user_id=uuid4(),
            get_credential_by_id=fake_get_credential_by_id,
            get_assistant_by_id=unexpected
        )


async def test_handle_get_messaging_credential_raises_when_not_owned():
    credential = make_credential()

    async def fake_get_credential_by_id(credential_id):
        return credential

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_get_messaging_credential(
            credential_id=credential.id,
            user_id=uuid4(),
            get_credential_by_id=fake_get_credential_by_id,
            get_assistant_by_id=fake_get_assistant_by_id
        )


async def test_handle_delete_messaging_credential_deletes_when_owned():
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    credential = make_credential(assistant_id=assistant.id)
    deleted: list = []

    async def fake_get_credential_by_id(credential_id):
        return credential

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return assistant

    async def fake_delete_credential_by_id(credential_id):
        deleted.append(credential_id)
        return credential

    await handle_delete_messaging_credential(
        credential_id=credential.id,
        user_id=user_id,
        get_credential_by_id=fake_get_credential_by_id,
        get_assistant_by_id=fake_get_assistant_by_id,
        delete_credential_by_id=fake_delete_credential_by_id
    )

    assert deleted == [credential.id]


async def test_handle_delete_messaging_credential_raises_when_credential_not_found():
    async def fake_get_credential_by_id(credential_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_delete_messaging_credential(
            credential_id=uuid4(),
            user_id=uuid4(),
            get_credential_by_id=fake_get_credential_by_id,
            get_assistant_by_id=unexpected,
            delete_credential_by_id=unexpected
        )


async def test_handle_delete_messaging_credential_raises_when_not_owned():
    credential = make_credential()

    async def fake_get_credential_by_id(credential_id):
        return credential

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_delete_messaging_credential(
            credential_id=credential.id,
            user_id=uuid4(),
            get_credential_by_id=fake_get_credential_by_id,
            get_assistant_by_id=fake_get_assistant_by_id,
            delete_credential_by_id=unexpected
        )


async def test_handle_delete_messaging_credential_raises_when_already_deleted():
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    credential = make_credential(assistant_id=assistant.id)

    async def fake_get_credential_by_id(credential_id):
        return credential

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return assistant

    async def fake_delete_credential_by_id(credential_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_delete_messaging_credential(
            credential_id=credential.id,
            user_id=user_id,
            get_credential_by_id=fake_get_credential_by_id,
            get_assistant_by_id=fake_get_assistant_by_id,
            delete_credential_by_id=fake_delete_credential_by_id
        )
