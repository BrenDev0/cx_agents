from datetime import datetime
from uuid import UUID

from .models import User
from .schemas import UserResponse
from src.cryptography.types import DecryptFn

def domain_to_public_schema(domain: User, decrypt: DecryptFn) -> UserResponse:
    return UserResponse(
        id=domain.id,
        email=decrypt(domain.email),
        created_at=domain.created_at
    )

def domain_to_cache_dict(domain: User) -> dict:
    return {
        "id": str(domain.id),
        "email": domain.email,
        "email_hash": domain.email_hash,
        "password": domain.password,
        "created_at": domain.created_at.isoformat()
    }

def cache_dict_to_domain(data: dict) -> User:
    return User(
        id=UUID(data["id"]),
        email=data["email"],
        email_hash=data["email_hash"],
        password=data["password"],
        created_at=datetime.fromisoformat(data["created_at"])
    )
