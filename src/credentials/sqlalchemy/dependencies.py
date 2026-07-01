from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request
from src.db.sqlalchemy.dependencies import get_db_session

from .repository import create, get_by_provider_external_id
from ..types import CreateCredentialFn, GetCredentialByExternalIdFn
from ..models import CredentialCreate, Credential, Provider




def provide_create_credential(db: AsyncSession = Depends(get_db_session)) -> CreateCredentialFn:
    async def create_credential(credential_in: CredentialCreate) -> Credential:
        return await create(db=db, credential_in=credential_in)

    return create_credential


def provide_get_credential_by_external_id(db: AsyncSession = Depends(get_db_session)) -> GetCredentialByExternalIdFn:
    async def  get_credential_by_external_id(provider: Provider, external_id: str) -> Credential | None:
        return await get_by_provider_external_id(db=db, provider=provider, external_id=external_id)

    return get_credential_by_external_id


async def get_agent_credential(
    request: Request,
    get_credential_by_external_id: GetCredentialByExternalIdFn = Depends(provide_get_credential_by_external_id)
) -> Credential:
    location_id = request.path_params.get("location_id", None)

    if not location_id:
        raise HTTPException(status_code=400, detail="No location id found in path")

    credential = await get_credential_by_external_id(Provider.GHL, location_id)

    if not credential:
        raise HTTPException(status_code=404, detail=f"No agent credential found for location id: {location_id}")

    return credential
