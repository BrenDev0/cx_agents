from dataclasses import asdict
from .models import CalendarRow
from ..models import Calendar, CalendarCreate, CalendarUpdate

def row_to_domain(row: CalendarRow) -> Calendar:
    return Calendar(
        id=row.id,
        assistant_id=row.assistant_id,
        calendar_id=row.calendar_id,
        timezone=row.timezone,
        required_fields=row.required_fields,
        title_template=row.title_template,
        updated_at=row.updated_at,
        created_at=row.created_at
    )

def domain_create_to_row(domain_create: CalendarCreate) -> CalendarRow:
    return CalendarRow(**asdict(domain_create))

def domain_update_to_values(domain_update: CalendarUpdate) -> dict:
    return asdict(domain_update)
