from typing import Callable, Awaitable
from .models import CredentialCreate, Credential, IntegrationProvider


CreateCredentialFn = Callable[[CredentialCreate], Awaitable[Credential]]
GetCredentialByExternalIdFn = Callable[[IntegrationProvider, str], Awaitable[Credential | None]]
