from uuid import UUID
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Provider(str, Enum):
    GHL = "ghl"


@dataclass(frozen=True)
class Credential:
    id: UUID
    assistant_id: UUID
    provider: Provider
    external_id: str
    payload: str
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class CredentialCreate:
    assistant_id: UUID
    provider: Provider
    external_id: str
    payload: str
    expires_at: datetime | None = None
