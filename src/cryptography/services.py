from .protocols import CryptographyService
from .types import EncryptFn, DecryptFn

class DefaultCryptographyService(CryptographyService):
    def __init__(
        self,
        encrypt: EncryptFn,
        decrypt: DecryptFn
    ):
        self._encrypt = encrypt
        self._decrypt = decrypt
    
    def encrypt(self, data: str | int):
        return self._encrypt(data)
    
    def decrypt(self, encrypted: str):
        return self._decrypt(encrypted)