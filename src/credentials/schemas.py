from pydantic import BaseModel
from uuid import UUID
from typing import Literal

from .models import Provider


class GhlCredentialPayload(BaseModel):
    provider: Literal[Provider.GHL] = Provider.GHL
    access_token: str
    location_id: str


class CreateCredentialRequest(BaseModel):
    assistant_id: UUID
    external_id: str
    payload: GhlCredentialPayload


class CredentialPublic(BaseModel):
    id: UUID
    assistant_id: UUID
    provider: Provider
    external_id: str
