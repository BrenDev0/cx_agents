from src.schemas import ApiSchema

class VerifyEmailRequest(ApiSchema):
    email: str


class RegistrationRequest(ApiSchema):
    email: str
    password: str
    verification_code: str | int


class LoginRequest(ApiSchema):
    email: str
    password: str