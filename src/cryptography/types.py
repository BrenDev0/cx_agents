from typing import Callable, Union
from typing import Protocol


EncryptFn = Callable[[str | int], str]
DecryptFn = Callable[[str], str]

class CryptographyService(Protocol):
    def encrypt(self, data: str | int) -> str: ...

    def decrypt(self ,encrypted: str) -> str: ...