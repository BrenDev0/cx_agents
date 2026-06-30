from enum import StrEnum
from uuid import UUID

class AuthCacheKey(StrEnum):
    VERIFICATION_CODE = "auth:registration:verification_code"
    VERIFICATION_ATTEMPTS = "auth:registration:attempts"
    REGISTRATION_BLOCKED = "auth:registration:blocked"
    LOGIN_ATTEMPS = "auth:login:attempts"
    LOGIN_BLOCKED = "auth:login:blocked"
    SESSION = "auth:session"


def get_verification_code_key(email_hash: str) -> str:
    return f"{email_hash}:{AuthCacheKey.VERIFICATION_CODE}"

def get_verification_attempts_key(email_hash: str) -> str:
    return f"{email_hash}:{AuthCacheKey.VERIFICATION_ATTEMPTS}"

def get_registration_blocked_key(email_hash: str) -> str:
    return f"{email_hash}:{AuthCacheKey.REGISTRATION_BLOCKED}"

def get_login_attemps_key(email: str) -> str:
    return f"{email}:{AuthCacheKey.LOGIN_ATTEMPS}"

def get_login_blocked_key(email: str) -> str:
    return f"{email}:{AuthCacheKey.LOGIN_BLOCKED}"

def get_session_key(session_id: UUID) -> str:
    return f"{AuthCacheKey.SESSION}:{session_id}"

def get_current_user_key(user_id: UUID) -> str:
    return f"{user_id}:auth:current_user"