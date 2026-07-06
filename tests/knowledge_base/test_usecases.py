from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.assistants.models import Assistant
from src.documents.models import Document
from src.exceptions import BadRequestException, ConflictException, NotFoundException
from src.knowledge_base.models import Knowledge, KnowledgeCreate, KnowledgeStatus
from src.knowledge_base.usecases import handle_create_knowledge, handle_list_assistant_knowledge


def make_document(**overrides) -> Document:
    defaults = dict(
        id=uuid4(),
        user_id=uuid4(),
        file_type="application/pdf",
        name="report.pdf",
        key="user/123-report.pdf",
        file_size=2048,
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return Document(**defaults)


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


@pytest.fixture
def mock_delay(monkeypatch) -> Mock:
    delay = Mock()
    monkeypatch.setattr("src.knowledge_base.usecases.add_document_to_knowledge_base.delay", delay)
    return delay


async def test_handle_create_knowledge_creates_pending_and_enqueues_task(mock_delay: Mock):
    user_id = uuid4()
    document = make_document(user_id=user_id)
    assistant = make_assistant(user_id=user_id)
    created: dict[str, KnowledgeCreate] = {}

    async def fake_get_document_by_id(document_id, user_id):
        assert document_id == document.id
        return document

    async def fake_get_assistant_by_id(assistant_id, user_id):
        assert assistant_id == assistant.id
        return assistant

    async def fake_get_knowledge_by_assistant_and_document(assistant_id, document_id):
        return None

    async def fake_create_knowledge(knowledge_in: KnowledgeCreate) -> Knowledge:
        created["knowledge_in"] = knowledge_in
        return Knowledge(
            id=uuid4(),
            assistant_id=knowledge_in.assistant_id,
            document_id=knowledge_in.document_id,
            status=knowledge_in.status,
            created_at=datetime.now(timezone.utc)
        )

    response = await handle_create_knowledge(
        document_id=document.id,
        assistant_id=assistant.id,
        user_id=user_id,
        get_document_by_id=fake_get_document_by_id,
        get_assistant_by_id=fake_get_assistant_by_id,
        get_knowledge_by_assistant_and_document=fake_get_knowledge_by_assistant_and_document,
        create_knowledge=fake_create_knowledge
    )

    assert response.assistant_id == assistant.id
    assert response.document_id == document.id
    assert response.status == KnowledgeStatus.PENDING
    assert created["knowledge_in"].status == KnowledgeStatus.PENDING
    mock_delay.assert_called_once_with(str(response.id), str(document.id), str(assistant.id), str(user_id))


async def test_handle_create_knowledge_raises_when_document_not_found(mock_delay: Mock):
    async def fake_get_document_by_id(document_id, user_id):
        return None

    async def unexpected(*args, **kwargs):
        raise AssertionError("should not be reached when document is missing")

    with pytest.raises(NotFoundException):
        await handle_create_knowledge(
            document_id=uuid4(),
            assistant_id=uuid4(),
            user_id=uuid4(),
            get_document_by_id=fake_get_document_by_id,
            get_assistant_by_id=unexpected,
            get_knowledge_by_assistant_and_document=unexpected,
            create_knowledge=unexpected
        )

    mock_delay.assert_not_called()


async def test_handle_create_knowledge_raises_when_document_is_not_pdf(mock_delay: Mock):
    document = make_document(file_type="text/plain")

    async def fake_get_document_by_id(document_id, user_id):
        return document

    async def unexpected(*args, **kwargs):
        raise AssertionError("should not be reached when document is not a pdf")

    with pytest.raises(BadRequestException):
        await handle_create_knowledge(
            document_id=document.id,
            assistant_id=uuid4(),
            user_id=document.user_id,
            get_document_by_id=fake_get_document_by_id,
            get_assistant_by_id=unexpected,
            get_knowledge_by_assistant_and_document=unexpected,
            create_knowledge=unexpected
        )

    mock_delay.assert_not_called()


async def test_handle_create_knowledge_raises_when_assistant_not_found(mock_delay: Mock):
    document = make_document()

    async def fake_get_document_by_id(document_id, user_id):
        return document

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return None

    async def unexpected(*args, **kwargs):
        raise AssertionError("should not be reached when assistant is missing")

    with pytest.raises(NotFoundException):
        await handle_create_knowledge(
            document_id=document.id,
            assistant_id=uuid4(),
            user_id=document.user_id,
            get_document_by_id=fake_get_document_by_id,
            get_assistant_by_id=fake_get_assistant_by_id,
            get_knowledge_by_assistant_and_document=unexpected,
            create_knowledge=unexpected
        )

    mock_delay.assert_not_called()


def make_knowledge(**overrides) -> Knowledge:
    defaults = dict(
        id=uuid4(),
        assistant_id=uuid4(),
        document_id=uuid4(),
        status=KnowledgeStatus.READY,
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return Knowledge(**defaults)


async def test_handle_list_assistant_knowledge_returns_mapped_responses():
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)
    knowledge_entries = [
        make_knowledge(assistant_id=assistant.id),
        make_knowledge(assistant_id=assistant.id)
    ]

    async def fake_get_assistant_by_id(assistant_id, user_id):
        assert assistant_id == assistant.id
        return assistant

    async def fake_get_knowledge_by_assistant_id(assistant_id):
        assert assistant_id == assistant.id
        return knowledge_entries

    response = await handle_list_assistant_knowledge(
        assistant_id=assistant.id,
        user_id=user_id,
        get_assistant_by_id=fake_get_assistant_by_id,
        get_knowledge_by_assistant_id=fake_get_knowledge_by_assistant_id
    )

    assert [r.id for r in response] == [k.id for k in knowledge_entries]
    assert all(r.assistant_id == assistant.id for r in response)


async def test_handle_list_assistant_knowledge_returns_empty_list_when_none_exist():
    user_id = uuid4()
    assistant = make_assistant(user_id=user_id)

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return assistant

    async def fake_get_knowledge_by_assistant_id(assistant_id):
        return []

    response = await handle_list_assistant_knowledge(
        assistant_id=assistant.id,
        user_id=user_id,
        get_assistant_by_id=fake_get_assistant_by_id,
        get_knowledge_by_assistant_id=fake_get_knowledge_by_assistant_id
    )

    assert response == []


async def test_handle_list_assistant_knowledge_raises_when_assistant_not_owned():
    async def fake_get_assistant_by_id(assistant_id, user_id):
        return None

    async def unexpected(*args, **kwargs):
        raise AssertionError("should not fetch knowledge when assistant ownership fails")

    with pytest.raises(NotFoundException):
        await handle_list_assistant_knowledge(
            assistant_id=uuid4(),
            user_id=uuid4(),
            get_assistant_by_id=fake_get_assistant_by_id,
            get_knowledge_by_assistant_id=unexpected
        )


async def test_handle_create_knowledge_raises_when_already_in_knowledge_base(mock_delay: Mock):
    user_id = uuid4()
    document = make_document(user_id=user_id)
    assistant = make_assistant(user_id=user_id)
    existing = Knowledge(
        id=uuid4(),
        assistant_id=assistant.id,
        document_id=document.id,
        status=KnowledgeStatus.READY,
        created_at=datetime.now(timezone.utc)
    )

    async def fake_get_document_by_id(document_id, user_id):
        return document

    async def fake_get_assistant_by_id(assistant_id, user_id):
        return assistant

    async def fake_get_knowledge_by_assistant_and_document(assistant_id, document_id):
        return existing

    async def unexpected(*args, **kwargs):
        raise AssertionError("should not create a duplicate knowledge entry")

    with pytest.raises(ConflictException):
        await handle_create_knowledge(
            document_id=document.id,
            assistant_id=assistant.id,
            user_id=user_id,
            get_document_by_id=fake_get_document_by_id,
            get_assistant_by_id=fake_get_assistant_by_id,
            get_knowledge_by_assistant_and_document=fake_get_knowledge_by_assistant_and_document,
            create_knowledge=unexpected
        )

    mock_delay.assert_not_called()
