from typing import Callable, Awaitable, Any
from .models import CredentialPartial, Credential


CreateCredentialFn = Callable[[CredentialPartial], Awaitable[Credential]]
GetCredentialByExternalIdFn = Callable[[str], Awaitable[Credential | None]]