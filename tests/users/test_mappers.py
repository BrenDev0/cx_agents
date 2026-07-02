from datetime import datetime, timezone
from uuid import uuid4

from src.users.mappers import domain_to_public_schema, domain_to_cache_dict, cache_dict_to_domain
from src.users.models import User, UserCreate
from src.users.sqlalchemy.mappers import domain_create_to_row, row_to_domain
from src.users.sqlalchemy.models import UserRow


def make_user(**overrides) -> User:
    defaults = dict(
        id=uuid4(),
        email="enc:user@example.com",
        email_hash="hash:user@example.com",
        password="hashed:correct-password",
        created_at=datetime.now(timezone.utc)
    )
    defaults.update(overrides)
    return User(**defaults)


def test_domain_to_public_schema_decrypts_email(fake_cryptography_service):
    user = make_user()

    result = domain_to_public_schema(user, decrypt=fake_cryptography_service.decrypt)

    assert result.id == user.id
    assert result.email == "user@example.com"
    assert result.created_at == user.created_at


def test_domain_to_cache_dict_serializes_fields():
    user = make_user()

    result = domain_to_cache_dict(user)

    assert result == {
        "id": str(user.id),
        "email": user.email,
        "email_hash": user.email_hash,
        "password": user.password,
        "created_at": user.created_at.isoformat()
    }


def test_cache_dict_to_domain_deserializes_fields():
    user = make_user()
    cache_dict = domain_to_cache_dict(user)

    result = cache_dict_to_domain(cache_dict)

    assert result == user


def test_domain_to_cache_dict_and_back_round_trips():
    user = make_user()

    assert cache_dict_to_domain(domain_to_cache_dict(user)) == user


def test_domain_create_to_row_maps_all_fields():
    user_create = UserCreate(
        email="enc:new@example.com",
        email_hash="hash:new@example.com",
        password="hashed:s3cret"
    )

    row = domain_create_to_row(user_create)

    assert isinstance(row, UserRow)
    assert row.email == user_create.email
    assert row.email_hash == user_create.email_hash
    assert row.password == user_create.password


def test_row_to_domain_maps_all_fields():
    row = UserRow(
        id=uuid4(),
        email="enc:user@example.com",
        email_hash="hash:user@example.com",
        password="hashed:correct-password",
        created_at=datetime.now(timezone.utc)
    )

    domain = row_to_domain(row)

    assert domain == User(
        id=row.id,
        email=row.email,
        email_hash=row.email_hash,
        password=row.password,
        created_at=row.created_at
    )
