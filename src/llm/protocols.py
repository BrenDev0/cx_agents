from typing import Protocol, TypeVar

T = TypeVar("T")

class Agent(Protocol):
    async def invoke(
        self, 
        message: list[dict]
    ) ->  str: ...

    async def invoke_structured(self, messages: list[dict], response_model: type[T]) -> T: ...

    def set_temperature(self, temperature: float): ...