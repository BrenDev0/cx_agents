from fastapi import APIRouter, Depends
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService

from .sqlalchemy.dependencies import provide_create_credential
from .types import CreateCredentialFn
from .schemas import CreateCredentialRequest
from .usecases import handle_create_credential


router = APIRouter(
    tags=["credentials"]
)


@router.post("", status_code=201)
async def credentials_create(
    data: CreateCredentialRequest,
    create_credential: CreateCredentialFn = Depends(provide_create_credential),
    cryptography: CryptographyService = Depends(get_cryptography_service)
): 
    return await handle_create_credential(
        credential_in=data,
        create_credential=create_credential,
        encryption=cryptography.encrypt
    )