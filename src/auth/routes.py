from fastapi import APIRouter, Depends, Request, Response
from uuid import UUID
from src.settings import settings
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService
from src.users.sqlalchemy.dependencies import provide_create_user
from src.cache.dependencies import get_cache_store
from src.cache.types import CacheStore
from src.users.schemas import UserResponse
from src.users.types import CreateUserFn
from .schemas import RegistrationRequest
from .usecases import handle_registration, create_session


router = APIRouter(
    tags=["Auth"]
)

async def _create_session_and_set_cookie(
    request: Request,
    response: Response,
    user_id: UUID,
    cache_store: CacheStore
):
    ip = getattr(request.state, "ip", "unknown")
    cleint_agent = getattr(request.headers, "client-agent")


    session_id = await create_session(
        cache_store=cache_store,
        user_id=user_id,
        ip=ip,
        client_agent=cleint_agent
    )

    response.set_cookie(
        key="session_id",
        value=str(session_id),
        max_age=60*60*24*7, # 7days
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )


# @router.post("/verification/email/onboarding", status_code=202)
# async def verify_email_for_onboarding():
#     pass


@router.post("", status_code=201, response_model=UserResponse)
async def registration(
    request: Request,
    response: Response,
    data: RegistrationRequest,
    create_user: CreateUserFn = Depends(provide_create_user),
    cache_store: CacheStore = Depends(get_cache_store),
    cryptography_service: CryptographyService = Depends(get_cryptography_service)
):
    user =  await handle_registration(
        data=data,
        cache_store=cache_store,
        create_user=create_user,
        cryptography_service=cryptography_service
    )

    await _create_session_and_set_cookie(
        request=request,
        response=response,
        user_id=user.id,
        cache_store=cache_store
    )

    return user


@router.post("/login", status_code=200)
async def login():
    pass


@router.post("/logout", status_code=200)
async def logout():
    pass