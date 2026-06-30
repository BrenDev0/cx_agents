from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Credential:
    id: UUID
    external_id: str
    access_token: str
    created_at: datetime


@dataclass(frozen=True)
class CredentialPartial:
    external_id: str
    access_token: str