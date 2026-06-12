from enum import StrEnum

from langchain_openai import ChatOpenAI


class Provider(StrEnum):
    OPENAI = "openai"

def get_model(model: str, provider: Provider, api_key: str):
    if provider == Provider.OPENAI:
        return ChatOpenAI(
            model=model,
            api_key=api_key
        )