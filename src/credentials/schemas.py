from pydantic import BaseModel

class CreateCredentialRequest(BaseModel):
    external_id: str
    access_token: str