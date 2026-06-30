from .types import CryptographyService
from .types import EncryptFn, DecryptFn, VerifyPasswordFn, DeterministicHashFn, HashPasswordFn

class DefaultCryptographyService:
    def __init__(
        self,
        encrypt: EncryptFn,
        decrypt: DecryptFn,
        verify_password: VerifyPasswordFn,
        deterministic_hash: DeterministicHashFn,
        hash_password: HashPasswordFn
    ):
        self._encrypt = encrypt
        self._decrypt = decrypt
        self._verify_password = verify_password
        self._determistic_hash = deterministic_hash
        self._hash_password = hash_password


    def encrypt(self, data: str | int):
        return self._encrypt(data)
    
    def decrypt(self, encrypted: str):
        return self._decrypt(encrypted)
    
    def verify_password(self, unhashed_password: str, hashed_password: str) -> bool:
        return self._verify_password(unhashed_password=unhashed_password, hashed_password=hashed_password)
    
    def deterministic_hash(self, str_to_hash: str) -> str:
        return self._determistic_hash(str_to_hash)
    
    def hash_password(self, str_to_hash) -> str:
        return self._hash_password(str_to_hash)