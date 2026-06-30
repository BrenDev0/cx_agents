from cryptography.fernet import Fernet
from src.settings import settings


def get_fernet() -> Fernet:
    return Fernet(settings.ENCRYPTION_KEY)


def encrypt(data: str | int) -> str:
    f = get_fernet()
    return f.encrypt(str(data).encode()).decode()


def decrypt(encrypted: str) -> str:
    f = get_fernet()
    return f.decrypt(encrypted.encode()).decode()