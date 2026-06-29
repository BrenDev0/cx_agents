from uuid import UUID
from dataclasses import asdict
from fastapi import Depends, Request
from src.users.sqlalchemy.dependencies import provide_get_user_by_id
from src.users.types import GetUserByIdFn
from src.users.models import User
from src.cache.types import CacheStore
from src.cache.dependencies import get_cache_store
from src.exceptions import UnauthorizedException
from .cache_keys import get_session_key, get_current_user_key



async def get_session_id(
    request: Request
) -> UUID:
    session_id = request.cookies.get("session_id")

    if not session_id:
        raise UnauthorizedException
    
    try:
        return UUID(session_id)
    
    except ValueError:
        raise UnauthorizedException


async def get_current_user(
    get_user_by_id: GetUserByIdFn = Depends(provide_get_user_by_id),
    cache_store: CacheStore = Depends(get_cache_store),
    session_id: UUID = Depends(get_session_id)
) -> User:
    session_key = get_session_key(session_id=session_id)

    session = await cache_store.get_json(key=session_key)
    if not session:
        raise UnauthorizedException
    
    user_id = session.get("user_id")

    if not user_id:
        raise UnauthorizedException
    
    current_user_cache_key = get_current_user_key(user_id=user_id)
    cached_user = await cache_store.get_json(current_user_cache_key)

    if cached_user:
        return User(cached_user)

    
    current_user = await get_user_by_id(user_id)

    if not current_user:
        raise UnauthorizedException

    await cache_store.store_json(
        key=current_user_cache_key,
        data=asdict(current_user),
        expire_seconds=60*5
    )


    return current_user

    


