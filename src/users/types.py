from typing import Callable, Awaitable
from .models import User, UserCreate


CreateUserFn = Callable[[UserCreate], Awaitable[User]]
