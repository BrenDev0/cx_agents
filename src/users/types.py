from typing import Callable, Awaitable
from uuid import UUID
from .models import User, UserCreate


CreateUserFn = Callable[[UserCreate], Awaitable[User]]
GetUserByIdFn = Callable[[UUID], Awaitable[User | None]]
GetUserByEmailHashFn = Callable[[str], Awaitable[User | None]]
