from fastapi import APIRouter, Depends

from .sqlalchemy.dependencies import provide_create_credential
from .types import CreateCredentialFn
from .schemas import CreateCredentialRequest

router = APIRouter(
    tags=["credentials"]
)


@router.post("", status_code=201)
async def credentials_create(
    data: CreateCredentialRequest,
    create_credential: CreateCredentialFn = Depends(provide_create_credential)
): 
    pass