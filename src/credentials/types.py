from typing import Callable, Awaitable
from .models import CredentialCreate, Credential, Provider


CreateCredentialFn = Callable[[CredentialCreate], Awaitable[Credential]]
GetCredentialByExternalIdFn = Callable[[Provider, str], Awaitable[Credential | None]]
