from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    email_hash: str
    password: str
    created_at: datetime


@dataclass(frozen=True)
class UserCreate:
    email: str
    email_hash: str
    password: str