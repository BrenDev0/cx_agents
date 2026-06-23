from typing import Callable, Awaitable, Any
from .models import CredentialPartial, Credential


CreateCredentialFn = Callable[[CredentialPartial], Awaitable[Credential]]