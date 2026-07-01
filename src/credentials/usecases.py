from src.cryptography.types import EncryptFn
from .models import CredentialCreate
from .types import CreateCredentialFn
from .schemas import CreateCredentialRequest, CredentialPublic


async def handle_create_credential(
    credential_in: CreateCredentialRequest,
    create_credential: CreateCredentialFn,
    encryption: EncryptFn
):
    prepared_data = CredentialCreate(
        assistant_id=credential_in.assistant_id,
        provider=credential_in.payload.provider,
        external_id=credential_in.external_id,
        payload=encryption(credential_in.payload.model_dump_json())
    )

    new_credential = await create_credential(prepared_data)

    return CredentialPublic(
        id=new_credential.id,
        assistant_id=new_credential.assistant_id,
        provider=new_credential.provider,
        external_id=new_credential.external_id
    )
