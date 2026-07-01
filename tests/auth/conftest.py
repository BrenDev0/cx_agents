from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.users.models import User


@pytest.fixture
def sample_user() -> User:
    return User(
        id=uuid4(),
        email="enc:user@example.com",
        email_hash="hash:user@example.com",
        password="hashed:correct-password",
        created_at=datetime.now(timezone.utc)
    )
