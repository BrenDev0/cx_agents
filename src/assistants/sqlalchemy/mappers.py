from dataclasses import asdict

from ..models import Assistant, AssistantCreate
from .models import AssistantRow


def row_to_domain(row: AssistantRow) -> Assistant:
    return Assistant(
        id=row.id,
        user_id=row.user_id,
        name=row.name,
        description=row.description,
        created_at=row.created_at
    )


def domain_create_to_row(domain_create: AssistantCreate) -> AssistantRow:
    return AssistantRow(**asdict(domain_create))