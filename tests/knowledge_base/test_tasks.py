from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from src.documents.models import Document
from src.knowledge_base.celery.tasks import _process_knowledge, EMBEDDING_BATCH_SIZE
from src.knowledge_base.models import KnowledgeStatus


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


@pytest.fixture
def update_status_mock(monkeypatch) -> AsyncMock:
    mock = AsyncMock()
    monkeypatch.setattr("src.knowledge_base.celery.tasks.update_status", mock)
    return mock


async def test_process_knowledge_happy_path_embeds_uploads_and_marks_ready(
    monkeypatch, fake_object_store, fake_embedding_service, fake_vector_store, fake_db, update_status_mock
):
    document = make_document(key="user/abc-report.pdf")
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.get_document_by_id",
        AsyncMock(return_value=document)
    )
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.extract_text_from_pdf",
        lambda file_bytes: "hello world, this is some extracted text"
    )

    knowledge_id = str(uuid4())
    document_id = str(document.id)
    assistant_id = str(uuid4())
    user_id = str(document.user_id)

    await _process_knowledge(knowledge_id, document_id, assistant_id, user_id)

    expected_metadata = {"user_id": user_id, "document_id": document_id, "assistant_id": assistant_id}

    assert fake_vector_store.deleted_filters == [expected_metadata]
    assert fake_object_store.downloaded_keys == ["user/abc-report.pdf"]
    assert len(fake_embedding_service.embed_chunks_calls) == 1
    texts, metadata = fake_embedding_service.embed_chunks_calls[0]
    assert texts == ["hello world, this is some extracted text"]
    assert metadata == expected_metadata
    assert len(fake_vector_store.upserted_results) == 1
    update_status_mock.assert_awaited_once_with(db=fake_db, knowledge_id=UUID(knowledge_id), status=KnowledgeStatus.READY)
    fake_db.commit.assert_awaited_once()
    fake_db.close.assert_awaited_once()
    assert fake_vector_store.closed is True


async def test_process_knowledge_splits_chunks_into_batches(
    monkeypatch, fake_object_store, fake_embedding_service, fake_vector_store, fake_db, update_status_mock
):
    document = make_document()
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.get_document_by_id",
        AsyncMock(return_value=document)
    )
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.extract_text_from_pdf",
        lambda file_bytes: "irrelevant text"
    )
    fake_chunks = [f"chunk-{i}" for i in range(EMBEDDING_BATCH_SIZE * 2 + 50)]
    monkeypatch.setattr("src.knowledge_base.celery.tasks.chunk_text", lambda text: fake_chunks)

    await _process_knowledge(str(uuid4()), str(document.id), str(uuid4()), str(document.user_id))

    batch_sizes = [len(texts) for texts, _ in fake_embedding_service.embed_chunks_calls]
    assert batch_sizes == [EMBEDDING_BATCH_SIZE, EMBEDDING_BATCH_SIZE, 50]
    assert len(fake_vector_store.upserted_results) == 3


async def test_process_knowledge_marks_failed_and_reraises_when_document_not_found(
    monkeypatch, fake_object_store, fake_embedding_service, fake_vector_store, fake_db, update_status_mock
):
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.get_document_by_id",
        AsyncMock(return_value=None)
    )

    knowledge_id = str(uuid4())

    with pytest.raises(ValueError):
        await _process_knowledge(knowledge_id, str(uuid4()), str(uuid4()), str(uuid4()))

    update_status_mock.assert_awaited_once_with(
        db=fake_db, knowledge_id=UUID(knowledge_id), status=KnowledgeStatus.FAILED
    )
    fake_db.rollback.assert_awaited_once()
    fake_db.close.assert_awaited_once()
    assert fake_object_store.downloaded_keys == []


async def test_process_knowledge_marks_failed_when_no_extractable_text(
    monkeypatch, fake_object_store, fake_embedding_service, fake_vector_store, fake_db, update_status_mock
):
    document = make_document()
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.get_document_by_id",
        AsyncMock(return_value=document)
    )
    monkeypatch.setattr("src.knowledge_base.celery.tasks.extract_text_from_pdf", lambda file_bytes: "   ")

    with pytest.raises(ValueError):
        await _process_knowledge(str(uuid4()), str(document.id), str(uuid4()), str(document.user_id))

    update_status_mock.assert_awaited_once()
    assert update_status_mock.await_args.kwargs["status"] == KnowledgeStatus.FAILED
    assert fake_embedding_service.embed_chunks_calls == []


async def test_process_knowledge_marks_failed_and_still_closes_vector_store_on_embedding_error(
    monkeypatch, fake_object_store, fake_embedding_service, fake_vector_store, fake_db, update_status_mock
):
    document = make_document()
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.get_document_by_id",
        AsyncMock(return_value=document)
    )
    monkeypatch.setattr(
        "src.knowledge_base.celery.tasks.extract_text_from_pdf",
        lambda file_bytes: "some real text"
    )

    async def failing_embed_chunks(texts, metadata=None):
        raise RuntimeError("embedding provider is down")

    fake_embedding_service.embed_chunks = failing_embed_chunks

    with pytest.raises(RuntimeError):
        await _process_knowledge(str(uuid4()), str(document.id), str(uuid4()), str(document.user_id))

    assert update_status_mock.await_args.kwargs["status"] == KnowledgeStatus.FAILED
    assert fake_vector_store.closed is True
    assert fake_vector_store.upserted_results == []
