from .models import User
from .schemas import UserResponse
from src.cryptography.types import DecryptFn

def domain_to_public_schema(domain: User, decrypt: DecryptFn) -> UserResponse:
    return UserResponse(
        id=domain.id,
        email=decrypt(domain.email),
        created_at=domain.created_at
    )
