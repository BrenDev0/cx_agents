from typing import Protocol

class Agent(Protocol):
    async def invoke():
        pass
