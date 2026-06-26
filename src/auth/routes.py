from fastapi import APIRouter, Depends, Request, Response

from .schemas import RegistrationRequest


router = APIRouter(
    tags=["Auth"]
)



# @router.post("/verification/email/onboarding", status_code=202)
# async def verify_email_for_onboarding():
#     pass


@router.post("", status_code=201)
async def registration(
    request: Request,
    data: RegistrationRequest
):
    pass


@router.post("/login", status_code=200)
async def login():
    pass


@router.post("/logout", status_code=200)
async def logout():
    pass