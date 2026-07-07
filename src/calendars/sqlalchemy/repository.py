from sqlalchemy import select, delete, update
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils import utc_now
from ..models import Calendar, CalendarCreate, CalendarUpdate
from .mappers import row_to_domain, domain_create_to_row, domain_update_to_values
from .models import CalendarRow


async def create(db: AsyncSession, calendar_in: CalendarCreate) -> Calendar:
    row = domain_create_to_row(calendar_in)
    db.add(row)
    await db.flush()
    await db.refresh(row)

    return row_to_domain(row)


async def get_by_assistant_id(db: AsyncSession, assistant_id: UUID) -> Calendar | None:
    stmt = select(CalendarRow).where(CalendarRow.assistant_id == assistant_id)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def update_by_assistant_id(db: AsyncSession, assistant_id: UUID, calendar_in: CalendarUpdate) -> Calendar | None:
    stmt = (
        update(CalendarRow)
        .where(CalendarRow.assistant_id == assistant_id)
        .values(**domain_update_to_values(calendar_in), updated_at=utc_now())
        .returning(CalendarRow)
    )

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None


async def delete_by_assistant_id(db: AsyncSession, assistant_id: UUID) -> Calendar | None:
    stmt = delete(CalendarRow).where(CalendarRow.assistant_id == assistant_id).returning(CalendarRow)

    result = await db.execute(stmt)

    row = result.scalar_one_or_none()

    return row_to_domain(row) if row else None
