from pydantic import BaseModel
from typing import Union

class RegistrationRequest(BaseModel):
    email: str
    password: str
    verification_code: Union[str, int]