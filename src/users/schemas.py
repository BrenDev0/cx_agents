from pydantic import BaseModel
from typing import Union
from uuid import UUID
from datetime import datetime

class UserCreateRequest(BaseModel):
    email: str
    password: str
    code: Union[str, int]


class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime