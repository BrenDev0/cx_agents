from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class AssistantSetting:
    id: UUID
    assistant_id: UUID
    personality: str
    instructions: str
    rules: str
    has_calendar: bool
    has_rag: bool
    updated_at: datetime
    created_at: datetime

@dataclass(frozen=True)
class AssistantSettingCreate:
    assistant_id: UUID
    personality: str = "You are a helpful and friendly assistant"
    instructions: str = "Assist the user in answering their queries the best you can"
    rules: str = "Always answer in the language of the conversation"
    has_calendar: bool = False
    has_rag: bool = False