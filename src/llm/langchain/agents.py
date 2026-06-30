from pydantic import SecretStr
from .models import get_model, Provider
from typing import TypeVar


T = TypeVar("T")

class LangchainAgent:
    def __init__(
        self,
        model: str,
        provider: Provider,
        api_key: SecretStr,
        temperature: float = 0.0,
    ):
        self._llm = get_model(
            model=model,
            provider=provider,
            api_key=api_key,
            temperature=temperature
        )

    def set_temperature(self, temperature: float):
        self._llm.temperature = temperature

    async def invoke(
        self,
        messages: list[dict]
    ) -> str:
        
        response = await self._llm.ainvoke(messages)
        content = str(response.content.strip())

        return content
    
    async def invoke_structured(
        self,
        messages: list[dict],
        response_model: type[T]
    ) -> T:
        structured_llm = self._llm.with_structured_output(response_model)

        response = await structured_llm.ainvoke(messages)

        return response

