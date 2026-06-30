from typing import Protocol, TypeVar
from src.types import ChatMessage

T = TypeVar("T")

class Agent(Protocol):
    async def invoke(
        self, 
        message: list[ChatMessage]
    ) ->  str: ...

    async def invoke_structured(self, messages: list[ChatMessage], response_model: type[T]) -> T: ...

    def set_temperature(self, temperature: float): ...