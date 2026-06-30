from pydantic import BaseModel
from uuid import UUID

class CreateCredentialRequest(BaseModel):
    external_id: str
    access_token: str

class CredentialPublic(BaseModel):
    id: UUID
    external_id: str