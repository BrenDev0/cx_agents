from enum import StrEnum
from pydantic import SecretStr
from langchain_openai import ChatOpenAI


class Provider(StrEnum):
    OPENAI = "openai"

def get_model(model: str, provider: str | Provider, api_key: SecretStr):
    provider= Provider(provider)
    if provider == Provider.OPENAI:
        return ChatOpenAI(
            model=model,
            api_key=api_key
        )