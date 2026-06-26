from uuid import UUID, uuid4
from src.cache.types import CacheStore
from src.users.schemas import UserResponse
from src.users.types import CreateUserFn
from src.users.mappers import domain_to_public_schema
from src.users.models import UserCreate
from src.cryptography.services import DefaultCryptographyService
from .schemas import RegistrationRequest
from .service import verify_code_or_raise
from .cahce_keys import get_session_key
from ..utils import utc_now_iso



async def handle_registration(
    data: RegistrationRequest,
    cache_store: CacheStore,
    create_user: CreateUserFn,
    cryptography_service: DefaultCryptographyService
) -> UserResponse:
    hashed_email = cryptography_service.deterministic_hash(data.email)
    
    await verify_code_or_raise(
        code_from_user=data.verification_code,
        email_hash=hashed_email,
        cache_store=cache_store
    )

    hashed_password = cryptography_service.hash_password(data.password)

    user_in = UserCreate(
        email=cryptography_service.encrypt(data.email),
        email_hash=hashed_email,
        password=hashed_password
    )

    new_user = await create_user(user_in)

    return domain_to_public_schema(domain=new_user, decrypt=cryptography_service.decrypt)



async def create_session(
    cache_store: CacheStore,
    user_id: UUID,
    ip: str,
    client_agent: str
) -> UUID: 
    session_id = uuid4()
    key = get_session_key(session_id)

    session_payload = {
        "user_id": str(user_id),
        "ip": ip,
        "client_agent": client_agent, 
        "created_at": utc_now_iso()
    }

    await cache_store.store_json(
        key=key,
        data=session_payload,
        expire_seconds=60*60*24*7 #7 days
    )

    return session_id





