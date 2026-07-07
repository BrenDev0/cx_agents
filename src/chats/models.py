from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class WebhookChannel(StrEnum):
    """Which integration a webhook is registered under -- distinct from
    MessagingChannel, which is the actual platform (sms/whatsapp/messenger)
    a given message travels over and is used for credential lookup."""
    GHL = "ghl"


@dataclass(frozen=True)
class ChatContext:
    assistant_id: UUID
    webhook_secret_hash: str
    credential: str
    has_calendar: bool
    has_rag: bool
    calendar_id: str | None
    timezone: str | None
    required_fields: list[str] | None
    title_template: str | None
