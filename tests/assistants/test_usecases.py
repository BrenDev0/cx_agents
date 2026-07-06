from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.assistants.models import Assistant
from src.assistants.usecases import handle_delete_assistant, handle_list_assistants
from src.exceptions import NotFoundException


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


async def test_handle_list_assistants_returns_mapped_responses():
    user_id = uuid4()
    assistants = [make_assistant(user_id=user_id), make_assistant(user_id=user_id)]

    async def fake_get_users_assistants(requested_user_id):
        assert requested_user_id == user_id
        return assistants

    response = await handle_list_assistants(
        user_id=user_id,
        get_users_assistants=fake_get_users_assistants
    )

    assert [r.id for r in response] == [a.id for a in assistants]
    assert [r.name for r in response] == [a.name for a in assistants]
    assert all(not hasattr(r, "webhook_secret_hash") for r in response)


async def test_handle_list_assistants_returns_empty_list_when_none_exist():
    async def fake_get_users_assistants(user_id):
        return []

    response = await handle_list_assistants(
        user_id=uuid4(),
        get_users_assistants=fake_get_users_assistants
    )

    assert response == []


async def test_handle_delete_assistant_deletes_when_owned():
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    deleted: list = []

    async def fake_delete_assistant_by_id(assistant_id, user_id):
        deleted.append((assistant_id, user_id))
        return assistant

    await handle_delete_assistant(
        assistant_id=assistant.id,
        user_id=user_id,
        delete_assistant_by_id=fake_delete_assistant_by_id
    )

    assert deleted == [(assistant.id, user_id)]


async def test_handle_delete_assistant_raises_when_not_found():
    async def fake_delete_assistant_by_id(assistant_id, user_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_delete_assistant(
            assistant_id=uuid4(),
            user_id=uuid4(),
            delete_assistant_by_id=fake_delete_assistant_by_id
        )
