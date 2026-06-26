from src.cache.types import CacheStore
from src.exceptions import BadRequestException, RequestBlockedException
from src.users.schemas import UserResponse
from src.users.types import CreateUserFn
from .cahce_keys import get_verification_code_key, get_verification_attempts_key, get_registration_blocked_key
from .schemas import RegistrationRequest




async def handle_registration(
    data: RegistrationRequest,
    cache_store: CacheStore,
    create_user: CreateUserFn
) -> UserResponse:
    pass