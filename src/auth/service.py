import asyncio
import secrets
from src.cache.types import CacheStore
from src.exceptions import RequestBlockedException, BadRequestException
from src.settings import settings
from .cache_keys import get_verification_attempts_key, get_registration_blocked_key, get_verification_code_key

async def ensure_not_blocked_from_registration(
    email_hash: str,
    cache_store: CacheStore
) -> bool:
    is_blocked_key = get_registration_blocked_key(email_hash=email_hash)
    registration_is_blocked = await cache_store.get_bool(is_blocked_key)

    if registration_is_blocked:
        raise  RequestBlockedException("Too many requests try again later")
    
    return True



async def verify_code_or_raise(
    code_from_user: str | int,
    email_hash: str,
    cache_store: CacheStore
) -> bool:
    await ensure_not_blocked_from_registration(email_hash=email_hash, cache_store=cache_store)

    verification_code_key = get_verification_code_key(email_hash=email_hash)
    attempts_key = get_verification_attempts_key(email_hash=email_hash)
    blocked_key = get_registration_blocked_key(email_hash=email_hash)

    verification_code = await cache_store.get_int(verification_code_key)

    if not verification_code:
        raise BadRequestException("Verification code expired")

    if int(code_from_user) != int(verification_code):
        attempts = await cache_store.increment(attempts_key)

        if int(attempts) >= int(settings.REGISTRATION_MAX_ATTEMPS):
            await asyncio.gather(
                cache_store.remove(verification_code_key),
                cache_store.remove(attempts_key),
                cache_store.store_bool(
                    key=blocked_key,
                    data=True,
                    expire_seconds=60 * 10
                )
            )

        raise BadRequestException("Incorrect verification code")

    await asyncio.gather(
        cache_store.remove(verification_code_key),
        cache_store.remove(attempts_key),
        cache_store.remove(blocked_key)
    )

    return True


def generate_random_code(
    length: int = 6
) -> int:
    min_value = 10 ** (length -1)
    max_value = (10 ** length) - 1
    
    return secrets.randbelow(max_value - min_value) + min_value
