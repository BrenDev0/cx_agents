from pydantic import BaseModel
from uuid import UUID
from typing import Literal

from .models import IntegrationProvider


class GhlCredentialPayload(BaseModel):
    provider: Literal[IntegrationProvider.GHL] = IntegrationProvider.GHL
    access_token: str
    location_id: str


class CreateCredentialRequest(BaseModel):
    assistant_id: UUID
    external_id: str
    payload: GhlCredentialPayload


class CredentialPublic(BaseModel):
    id: UUID
    assistant_id: UUID
    provider: IntegrationProvider
    external_id: str
