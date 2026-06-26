from src.cache.types import CacheStore

from src.users.schemas import UserResponse
from src.users.types import CreateUserFn
from .cahce_keys import get_verification_code_key, get_verification_attempts_key, get_registration_blocked_key
from .schemas import RegistrationRequest

async def _verify_code(
    verification_code: str | int, 
    email_hash: str,
    cache_store: CacheStore
) -> bool:
    is_blocked_key = get_registration_blocked_key(email_hash=email_hash)
    registration_is_blocked = await cache_store.get(is_blocked_key)

    if registration_is_blocked:
        raise  



async def handle_registration(
    data: RegistrationRequest,
    cache_store: CacheStore,
    create_user: CreateUserFn
) -> UserResponse:
    pass