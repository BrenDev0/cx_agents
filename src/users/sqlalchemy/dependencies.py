from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import create
from ..types import CreateUserFn
from ..models import UserCreate, User

def provide_create_user(db: AsyncSession) -> CreateUserFn:
    async def create_user(user_in: UserCreate) -> User:
        return create(db=db, user_in=user_in)
    
    return create_user

