from pydantic import BaseModel


class AssistantCreateRequest(BaseModel):
    name: str
    description: str