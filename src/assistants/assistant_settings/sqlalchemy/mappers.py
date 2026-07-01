from dataclasses import asdict
from .models import AssistantSettingsRow
from ..models import AssistantSetting, AssistantSettingCreate, AssistantSettingUpdate

def row_to_domain(row: AssistantSettingsRow) -> AssistantSetting:
    return AssistantSetting(
        id=row.id,
        assistant_id=row.assistant_id,
        personality=row.personality,
        instructions=row.instructions,
        rules=row.rules,
        has_calendar=row.has_calendar,
        has_rag=row.has_rag,
        updated_at=row.updated_at,
        created_at=row.created_at
    )

def domain_create_to_row(domain_create: AssistantSettingCreate) -> AssistantSettingsRow:
    return AssistantSettingsRow(**asdict(domain_create))

def domain_update_to_values(domain_update: AssistantSettingUpdate) -> dict:
    return asdict(domain_update)