from typing import Callable, Protocol


EncryptFn = Callable[[str | int], str]
DecryptFn = Callable[[str], str]
DeterministicHashFn = Callable[[str], str]
HashPasswordFn = Callable[[str], str]


class VerifyPasswordFn(Protocol):
    def __call__(
        self, 
        unhashed_password: str, 
        hashed_password: str
    ) -> bool: ...


class CryptographyService(Protocol):
    def encrypt(self, data: str | int) -> str: ...

    def decrypt(self, encrypted: str) -> str: ...

    def deterministic_hash(self, value: str) -> str: ...
    
    def hash_password(self, str_to_hash: str) -> str: ...

    def verify_password(self, unhashed_password: str, hashed_password: str) -> bool: ...