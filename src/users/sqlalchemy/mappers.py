from dataclasses import asdict

from .models import UserRow
from ..models import User, UserCreate


def domain_create_to_row(domain_create: UserCreate) -> UserRow:
    return UserRow(**asdict(domain_create))


def row_to_domain(row: UserRow) -> User:
    return User(
        id=row.id,
        email=row.email,
        email_hash=row.email_hash,
        password=row.password,
        created_at=row.created_at
    )