from src.cryptography.types import EncryptFn
from .models import Credential, CredentialPartial
from .types import CreateCredentialFn
from .schemas import CreateCredentialRequest


async def handle_create_credential(
    credential_in: CreateCredentialRequest,
    create_credential: CreateCredentialFn,
    encryption: EncryptFn
): 
    prepared_data = CredentialPartial(
        external_id=credential_in.external_id,
        access_token=encryption(credential_in.access_token)
    )

    new_credential = await create_credential(prepared_data)

    return 
    
    