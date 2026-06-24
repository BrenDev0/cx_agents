from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.db.dependencies import get_db_session

from .repository import create
from ..types import CreateCredentialFn
from ..models import CredentialPartial, Credential




def provide_create_credential(db: AsyncSession = Depends(get_db_session)) -> CreateCredentialFn:
    async def create_credential(credential_in: CredentialPartial) -> Credential:
        return await create(db=db, credential_in=credential_in)
    
    return create_credential