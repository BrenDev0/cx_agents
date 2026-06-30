from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID 

from src.db.sqlalchemy.dependencies import get_db_session
from .repository import create, get_by_email_hash, get_by_id
from ..types import CreateUserFn, GetUserByEmailHashFn, GetUserByIdFn
from ..models import UserCreate, User

def provide_create_user(db: AsyncSession = Depends(get_db_session)) -> CreateUserFn:
    async def create_user(user_in: UserCreate) -> User:
        return await create(db=db, user_in=user_in)
    
    return create_user

def provide_get_user_by_id(db: AsyncSession = Depends(get_db_session)) -> GetUserByIdFn:
    async def get_user_by_id(user_id: UUID) -> User | None:
        return await get_by_id(db=db, user_id=user_id)
    
    return get_user_by_id

def provide_get_user_by_email_hash(db: AsyncSession = Depends(get_db_session)) -> GetUserByEmailHashFn:
    async def get_user_by_email_hash(email_hash: str) -> User | None:
        return await get_by_email_hash(db=db, email_hash=email_hash)
    
    return get_user_by_email_hash

