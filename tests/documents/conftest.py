import pytest


class FakeObjectStore:
    """In-memory stand-in for the ObjectStore protocol so usecases tests don't
    touch real AWS/S3."""

    def __init__(self) -> None:
        self.uploaded: dict[str, bytes] = {}
        self.deleted: list[str] = []

    async def upload(self, key: str, file_bytes: bytes) -> str:
        self.uploaded[key] = file_bytes
        return f"https://example.com/{key}"

    async def get_object(self, key: str, expires_in: int = 900) -> str:
        return f"https://example.com/{key}?expires_in={expires_in}"

    async def delete_object(self, key: str) -> bool:
        self.deleted.append(key)
        return True


@pytest.fixture
def fake_object_store() -> FakeObjectStore:
    return FakeObjectStore()


class FakeVectorStore:
    """In-memory stand-in for the VectorStore protocol so usecases tests don't
    touch real Qdrant."""

    def __init__(self) -> None:
        self.deleted_filters: list[dict] = []

    async def delete_by_filter(self, filter: dict) -> bool:
        self.deleted_filters.append(filter)
        return True


@pytest.fixture
def fake_vector_store() -> FakeVectorStore:
    return FakeVectorStore()
