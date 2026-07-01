from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.auth.cache_keys import get_verification_code_key, get_session_key
from src.auth.schemas import RegistrationRequest, LoginRequest
from src.auth.usecases import handle_registration, handle_login, create_session
from src.exceptions import BadRequestException
from src.users.models import User, UserCreate


async def test_handle_registration_creates_user_and_returns_decrypted_email(
    fake_cache_store, fake_cryptography_service
):
    email = "new@example.com"
    email_hash = fake_cryptography_service.deterministic_hash(email)
    await fake_cache_store.store_int(key=get_verification_code_key(email_hash), data=111111, expire_seconds=60)

    created: dict[str, UserCreate] = {}

    async def fake_create_user(user_in: UserCreate) -> User:
        created["user_in"] = user_in
        return User(
            id=uuid4(),
            email=user_in.email,
            email_hash=user_in.email_hash,
            password=user_in.password,
            created_at=datetime.now(timezone.utc)
        )

    data = RegistrationRequest(email=email, password="s3cret", verification_code="111111")

    response = await handle_registration(
        data=data,
        cache_store=fake_cache_store,
        create_user=fake_create_user,
        cryptography_service=fake_cryptography_service
    )

    assert response.email == email
    assert created["user_in"].email_hash == email_hash
    assert created["user_in"].password == fake_cryptography_service.hash_password("s3cret")


async def test_handle_registration_raises_on_bad_code_and_does_not_create_user(
    fake_cache_store, fake_cryptography_service
):
    async def fake_create_user(user_in: UserCreate) -> User:
        raise AssertionError("create_user should not be called when verification fails")

    data = RegistrationRequest(email="new@example.com", password="s3cret", verification_code="000000")

    with pytest.raises(BadRequestException):
        await handle_registration(
            data=data,
            cache_store=fake_cache_store,
            create_user=fake_create_user,
            cryptography_service=fake_cryptography_service
        )


async def test_handle_login_success_returns_decrypted_email(fake_cryptography_service, sample_user):
    async def fake_get_user_by_email_hash(email_hash: str) -> User | None:
        assert email_hash == sample_user.email_hash
        return sample_user

    data = LoginRequest(email="user@example.com", password="correct-password")

    response = await handle_login(
        login_data=data,
        cryptography_service=fake_cryptography_service,
        get_user_by_email_hash=fake_get_user_by_email_hash
    )

    assert response.id == sample_user.id
    assert response.email == "user@example.com"


async def test_handle_login_raises_when_user_not_found(fake_cryptography_service):
    async def fake_get_user_by_email_hash(email_hash: str) -> User | None:
        return None

    data = LoginRequest(email="missing@example.com", password="whatever")

    with pytest.raises(BadRequestException):
        await handle_login(
            login_data=data,
            cryptography_service=fake_cryptography_service,
            get_user_by_email_hash=fake_get_user_by_email_hash
        )


async def test_handle_login_raises_on_wrong_password(fake_cryptography_service, sample_user):
    async def fake_get_user_by_email_hash(email_hash: str) -> User | None:
        return sample_user

    data = LoginRequest(email="user@example.com", password="wrong-password")

    with pytest.raises(BadRequestException):
        await handle_login(
            login_data=data,
            cryptography_service=fake_cryptography_service,
            get_user_by_email_hash=fake_get_user_by_email_hash
        )


async def test_create_session_stores_payload_and_returns_uuid(fake_cache_store):
    user_id = uuid4()

    session_id = await create_session(
        cache_store=fake_cache_store,
        user_id=user_id,
        ip="127.0.0.1",
        client_agent="pytest"
    )

    stored = await fake_cache_store.get_json(get_session_key(session_id))

    assert stored["user_id"] == str(user_id)
    assert stored["ip"] == "127.0.0.1"
    assert stored["client_agent"] == "pytest"
