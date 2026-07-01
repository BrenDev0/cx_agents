from sqlalchemy import select, delete, update
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils import utc_now
from ..models import AssistantSetting, AssistantSettingCreate, AssistantSettingUpdate
from .mappers import row_to_domain, domain_create_to_row, domain_update_to_values
from .models import AssistantSettingsRow


async def create(db: AsyncSession, assistant_setting_in: AssistantSettingCreate) -> AssistantSetting:
    row = domain_create_to_row(assistant_setting_in)
    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_assistant_id(db: AsyncSession, assistant_id: UUID) -> AssistantSetting | None:
    stmt = select(AssistantSettingsRow).where(AssistantSettingsRow.assistant_id == assistant_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def update_by_assistant_id(db: AsyncSession, assistant_id: UUID, assistant_setting_in: AssistantSettingUpdate) -> AssistantSetting | None:
    stmt = (
        update(AssistantSettingsRow)
        .where(AssistantSettingsRow.assistant_id == assistant_id)
        .values(**domain_update_to_values(assistant_setting_in), updated_at=utc_now())
        .returning(AssistantSettingsRow)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def delete_by_assistant_id(db: AsyncSession, assistant_id: UUID) -> AssistantSetting | None:
    stmt = delete(AssistantSettingsRow).where(AssistantSettingsRow.assistant_id == assistant_id).returning(AssistantSettingsRow)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None
