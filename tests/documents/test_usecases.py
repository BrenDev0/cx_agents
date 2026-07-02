from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.documents.models import Document, DocumentCreate
from src.documents.usecases import handle_upload, handle_get_document, handle_delete_document
from src.exceptions import NotFoundException


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


async def test_handle_upload_creates_document_and_uploads_bytes(fake_object_store):
    user_id = uuid4()
    created: dict[str, DocumentCreate] = {}

    async def fake_create_document(document_in: DocumentCreate) -> Document:
        created["document_in"] = document_in
        return make_document(
            user_id=document_in.user_id,
            file_type=document_in.file_type,
            name=document_in.name,
            key=document_in.key,
            file_size=document_in.file_size
        )

    response = await handle_upload(
        user_id=user_id,
        object_store=fake_object_store,
        create_document=fake_create_document,
        filename="report.pdf",
        content_type="application/pdf",
        file_bytes=b"hello world"
    )

    assert response.name == "report.pdf"
    assert response.file_type == "application/pdf"
    assert response.file_size == len(b"hello world")
    assert created["document_in"].user_id == user_id
    assert created["document_in"].key in fake_object_store.uploaded
    assert fake_object_store.uploaded[created["document_in"].key] == b"hello world"


async def test_handle_upload_object_key_is_namespaced_by_user_and_unique():
    user_id = uuid4()
    keys_seen = []

    async def fake_create_document(document_in: DocumentCreate) -> Document:
        keys_seen.append(document_in.key)
        return make_document(user_id=document_in.user_id, key=document_in.key)

    class NoopObjectStore:
        async def upload(self, key, file_bytes):
            return "url"

        async def get_object(self, key, expires_in=900):
            return "url"

        async def delete_object(self, key):
            return True

    await handle_upload(
        user_id=user_id,
        object_store=NoopObjectStore(),
        create_document=fake_create_document,
        filename="a.pdf",
        content_type="application/pdf",
        file_bytes=b"data"
    )
    await handle_upload(
        user_id=user_id,
        object_store=NoopObjectStore(),
        create_document=fake_create_document,
        filename="a.pdf",
        content_type="application/pdf",
        file_bytes=b"data"
    )

    assert all(key.startswith(f"{user_id}/") for key in keys_seen)
    assert keys_seen[0] != keys_seen[1]


async def test_handle_upload_raises_runtime_error_when_storage_upload_fails():
    async def fake_create_document(document_in: DocumentCreate) -> Document:
        return make_document(key=document_in.key)

    class FailingObjectStore:
        async def upload(self, key, file_bytes):
            raise ConnectionError("storage unavailable")

        async def get_object(self, key, expires_in=900):
            raise AssertionError("should not be called")

        async def delete_object(self, key):
            raise AssertionError("should not be called")

    with pytest.raises(RuntimeError):
        await handle_upload(
            user_id=uuid4(),
            object_store=FailingObjectStore(),
            create_document=fake_create_document,
            filename="report.pdf",
            content_type="application/pdf",
            file_bytes=b"data"
        )


async def test_handle_get_document_returns_response_with_signed_url(fake_object_store):
    document = make_document()

    async def fake_get_document_by_id(document_id, user_id):
        assert document_id == document.id
        assert user_id == document.user_id
        return document

    response = await handle_get_document(
        document_id=document.id,
        user_id=document.user_id,
        object_store=fake_object_store,
        get_document_by_id=fake_get_document_by_id
    )

    assert response.id == document.id
    assert response.url == f"https://example.com/{document.key}?expires_in=900"


async def test_handle_get_document_raises_when_not_found(fake_object_store):
    async def fake_get_document_by_id(document_id, user_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_get_document(
            document_id=uuid4(),
            user_id=uuid4(),
            object_store=fake_object_store,
            get_document_by_id=fake_get_document_by_id
        )


async def test_handle_delete_document_deletes_from_storage(fake_object_store):
    document = make_document()

    async def fake_delete_document_by_id(document_id, user_id):
        assert document_id == document.id
        assert user_id == document.user_id
        return document

    await handle_delete_document(
        document_id=document.id,
        user_id=document.user_id,
        object_store=fake_object_store,
        delete_document_by_id=fake_delete_document_by_id
    )

    assert fake_object_store.deleted == [document.key]


async def test_handle_delete_document_raises_when_not_found(fake_object_store):
    async def fake_delete_document_by_id(document_id, user_id):
        return None

    with pytest.raises(NotFoundException):
        await handle_delete_document(
            document_id=uuid4(),
            user_id=uuid4(),
            object_store=fake_object_store,
            delete_document_by_id=fake_delete_document_by_id
        )

    assert fake_object_store.deleted == []


async def test_handle_delete_document_raises_runtime_error_when_storage_delete_fails():
    document = make_document()

    async def fake_delete_document_by_id(document_id, user_id):
        return document

    class FailingObjectStore:
        async def upload(self, key, file_bytes):
            raise AssertionError("should not be called")

        async def get_object(self, key, expires_in=900):
            raise AssertionError("should not be called")

        async def delete_object(self, key):
            raise ConnectionError("storage unavailable")

    with pytest.raises(RuntimeError):
        await handle_delete_document(
            document_id=document.id,
            user_id=document.user_id,
            object_store=FailingObjectStore(),
            delete_document_by_id=fake_delete_document_by_id
        )
