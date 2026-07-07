from uuid import UUID

from .models import ChatContext


def domain_to_cache_dict(domain: ChatContext) -> dict:
    return {
        "assistant_id": str(domain.assistant_id),
        "webhook_secret_hash": domain.webhook_secret_hash,
        "credential": domain.credential,
        "has_calendar": domain.has_calendar,
        "has_rag": domain.has_rag,
        "calendar_id": domain.calendar_id,
        "timezone": domain.timezone,
        "required_fields": domain.required_fields,
        "title_template": domain.title_template
    }


def cache_dict_to_domain(data: dict) -> ChatContext:
    return ChatContext(
        assistant_id=UUID(data["assistant_id"]),
        webhook_secret_hash=data["webhook_secret_hash"],
        credential=data["credential"],
        has_calendar=data["has_calendar"],
        has_rag=data["has_rag"],
        calendar_id=data.get("calendar_id"),
        timezone=data.get("timezone"),
        required_fields=data.get("required_fields"),
        title_template=data.get("title_template")
    )
