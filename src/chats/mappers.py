from uuid import UUID

from .models import ChatContext


def domain_to_cache_dict(domain: ChatContext) -> dict:
    return {
        "assistant_id": str(domain.assistant_id),
        "webhook_secret_hash": domain.webhook_secret_hash,
        "credential": domain.credential,
        "has_calendar": domain.has_calendar,
        "has_rag": domain.has_rag
    }


def cache_dict_to_domain(data: dict) -> ChatContext:
    return ChatContext(
        assistant_id=UUID(data["assistant_id"]),
        webhook_secret_hash=data["webhook_secret_hash"],
        credential=data["credential"],
        has_calendar=data["has_calendar"],
        has_rag=data["has_rag"]
    )
