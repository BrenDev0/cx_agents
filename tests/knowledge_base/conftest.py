from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.vector_store.models import DocumentChunk, EmbeddingResult


class FakeObjectStore:
    def __init__(self, **kwargs):
        self.downloaded_keys: list[str] = []
        self.bytes_to_return = b"%PDF-fake-bytes%"

    async def download(self, key: str) -> bytes:
        self.downloaded_keys.append(key)
        return self.bytes_to_return


class FakeEmbeddingService:
    def __init__(self, **kwargs):
        self.embed_chunks_calls: list[tuple[list[str], dict]] = []

    async def embed_chunks(self, texts: list[str], metadata=None) -> EmbeddingResult:
        self.embed_chunks_calls.append((texts, metadata))
        return EmbeddingResult(
            chunks=[DocumentChunk(content=text, metadata=metadata or {}, chunk_id=uuid4()) for text in texts],
            embeddings=[[0.0] for _ in texts]
        )


class FakeKnowledgeVectorStore:
    def __init__(self, **kwargs):
        self.deleted_filters: list[dict] = []
        self.upserted_results: list[EmbeddingResult] = []
        self.closed = False

    async def delete_by_filter(self, filter: dict) -> bool:
        self.deleted_filters.append(filter)
        return True

    async def upsert(self, result: EmbeddingResult) -> None:
        self.upserted_results.append(result)

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def fake_object_store(monkeypatch) -> FakeObjectStore:
    store = FakeObjectStore()
    monkeypatch.setattr("src.knowledge_base.celery.tasks.AwsObjectStore", lambda **kwargs: store)
    return store


@pytest.fixture
def fake_embedding_service(monkeypatch) -> FakeEmbeddingService:
    service = FakeEmbeddingService()
    monkeypatch.setattr("src.knowledge_base.celery.tasks.OpenaiEmbeddingService", lambda **kwargs: service)
    return service


@pytest.fixture
def fake_vector_store(monkeypatch) -> FakeKnowledgeVectorStore:
    store = FakeKnowledgeVectorStore()
    monkeypatch.setattr("src.knowledge_base.celery.tasks.QdrantVectorStore", lambda **kwargs: store)
    return store


@pytest.fixture
def fake_db(monkeypatch) -> AsyncMock:
    db = AsyncMock()
    monkeypatch.setattr("src.knowledge_base.celery.tasks.db_session_maker", lambda: db)
    return db
