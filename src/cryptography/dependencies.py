from fastapi import Request
from .types import CryptographyService

def get_cryptography_service(request: Request) -> CryptographyService:
    service = getattr(request.app.state, "cryptography", None)
    if not service:
        raise ValueError("Cryptography service not initialized in app")
    
    return service